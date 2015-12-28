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


def send(data, config):
    notify_fcns = {
        'json': notify_json,
        'slack': notify_slack,
        'email': notify_email,
    }

    data['instances'] = cleanup_statuses(data['instances'])

    for key, fcn in notify_fcns.iteritems():
        if key in config:
            fcn(data, config[key])


def notify_json(data, config):
    if 'file' in config:
        with open(config['file'], 'w') as fp:
            json.dump(data, fp, indent=4, sort_keys=True, default=json_serialize)
    else:
        print json.dumps(data, indent=4, sort_keys=True, default=json_serialize)


def notify_slack(data, config):
    # Don't spam slack if there's nothing wrong
    if not len(data['instances']):
        return

    instances = ', '.join(data['instances'].keys())
    post_data = {
        'text': '!!! %d instance(s) have an issue: %s' % (
            len(data['instances']), instances)
    }

    # Add in the optional keys
    if 'user_name' in config:
        post_data['username'] = config['user_name']

    if 'channel' in config:
        post_data['channel'] = config['channel']

    res = requests.post(config['hook_url'], json=post_data)
    res.raise_for_status()


def notify_email(data, config):

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
            '- %s: %s' % (name, ', '.join(inst))
            for name, inst in data['profiles']
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
