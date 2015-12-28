import json

import requests


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
            json.dump(data, fp, indent=4, sort_keys=True)
    else:
        print json.dumps(data, indent=4, sort_keys=True)


def notify_slack(data, config):
    # Don't spam slack if there's nothing wrong
    if not len(data['instances']):
        return

    instances = ', '.join(data['instances'].keys())
    text = "!!! %d instance(s) have an issue: %s" % (
        len(data['instances']), instances)

    res = requests.post(config['hook_url'], json={
        'username': config.get('username', 'Pension Bot'),
        'channel': config['channel'],
        'text': text
    })

    print 'Uh oh: ', res.text


def notify_email(statuses, config):
    pass
