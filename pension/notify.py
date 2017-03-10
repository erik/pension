import email
import json
import smtplib

from email.MIMEText import MIMEText

import requests


def json_serialize(obj):
    """handle datetime objects"""

    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON \
serializable' % (type(obj), repr(obj))


def cleanup_statuses(statuses):
    """Downcase keys and only include relevant items"""

    def _format_item(item):
        status = {'status': item['Status']}
        status.update({
            e['Name']: e['Status'] for e in item['Details']
        })

        return status

    info = {}

    for status in statuses:
        instance = status['InstanceId']
        status = {
            'events': status.get('Events', []),
            'instance': _format_item(status['InstanceStatus']),
            'system': _format_item(status['SystemStatus']),
        }

        info[instance] = status

    return info


def send(data, inst_map, config):
    notify_fcns = {
        'json': notify_json,
        'slack': notify_slack,
        'email': notify_email,
    }

    # Don't notify unless there's actually something wrong
    if not len(data['instances']):
        return

    data['instances'] = cleanup_statuses(data['instances'])

    for key, fcn in notify_fcns.iteritems():
        if key in config:
            fcn(data, inst_map, config[key])


def notify_json(data, inst_map, config):
    if 'file' in config:
        with open(config['file'], 'w') as fp:
            json.dump(data, fp, indent=4, sort_keys=True, default=json_serialize)
    else:
        print json.dumps(data, indent=4, sort_keys=True, default=json_serialize)


def notify_slack(data, inst_map, config):
    console_url = '{inst_name} (<https://{region}.console.aws.amazon.com/ec2/v2/home?\
region={region}#Instances:search={instance}|{instance}>)'

    # This is kind of a gross API.
    tags = {
        inst_id: {t['Key']: t['Value'] for t in inst.tags}
        for inst_id, inst in inst_map.iteritems()
    }

    instance_links = [
        console_url.format(
            region=profile['region'],
            instance=inst_id,
            inst_name=tags[inst_id].get('Name', 'unnamed'))
        for profile in data['profiles'].values()
        for inst_id in profile['instances']
    ]

    post_data = {
        'text': '%d instance(s) have an issue: %s' % (
            len(data['instances']), ', '.join(instance_links))
    }

    # Add in the optional keys
    if 'user_name' in config:
        post_data['username'] = config['user_name']

    if 'channel' in config:
        post_data['channel'] = config['channel']

    res = requests.post(config['hook_url'], json=post_data)
    res.raise_for_status()


def notify_email(data, inst_map, config):

    msg_content = '''
    {num_instances} EC2 instances currently have issues!
    ========

    By AWS profile:
    --------

    {profile_counts}

    Full details:
    --------

    {details}
    '''.format(
        num_instances=len(data['instances']),
        profile_counts='\n'.join([
            '- [%s] %s: %s' % (data['region'], name, ', '.join(data['instances']))
            for name, data in data['profiles'].iteritems()
        ]),
        details=json.dumps(data, indent=4, sort_keys=True, default=json_serialize)
    )

    msg = MIMEText(msg_content, 'plain')
    msg['Subject'] = config['subject']
    msg['From'] = config.get('sender', config['user_name'])
    msg['To'] = ', '.join(config['recipients'])

    smtp = smtplib.SMTP_SSL(config['server'])
    smtp.login(config['user_name'], config['password'])
    smtp.sendmail(config['sender'], config['recipients'], msg.as_string())
    smtp.close()
