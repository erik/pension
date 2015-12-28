import os
import os.path

from boto3.session import Session
import click
import toml

import notify


def get_profiles(config):
    if 'aws_profiles' not in config:
        return {
            'default': Session().client('ec2')
        }

    return {
        prof: Session(profile_name=prof).client('ec2')
        for prof in config['aws_profiles']
    }


def get_instance_statuses(ec2_client, config):
    def _filter(filters):
        _statuses = []
        next_token = ''

        while True:
            res = ec2_client.describe_instance_status(
                Filters=[
                    {'Name': k, 'Values': v}
                    for k, v in filters.iteritems()
                ],
                NextToken=next_token,
                MaxResults=1000
            )

            _statuses.extend(res['InstanceStatuses'])
            next_token = res.get('NextToken')

            if not next_token:
                break

        return _statuses

    # describe_instance_status is an AND of filters, we want an OR
    seen = set()
    results = [
        _filter({'event.code': ['*']}),
        _filter({'instance-status.status': ['impaired']}),
        _filter({'instance-status.reachability': ['failed']}),
        _filter({'system-status.status': ['impaired']}),
        _filter({'system-status.reachability': ['failed']}),
    ]

    statuses = []
    for instances in results:
        statuses.extend([i for i in instances if i['InstanceId'] not in seen])
        seen.update([i['InstanceId'] for i in instances])

    return statuses


def get_config(config_locations):
    for loc in config_locations:
        file_name = os.path.expanduser(loc)

        if os.path.exists(file_name):
            click.echo('using config %s' % file_name, err=True)

            with open(file_name) as fp:
                return toml.loads(fp.read())


@click.command()
@click.option('--dry-run', is_flag=True, help='Disables sending alerts')
@click.option('--config', required=False, help='Configuration file location')
@click.option('--quiet', '-q', is_flag=True, help='Disables default JSON output')
def main(dry_run, config, quiet):
    config_names = [config] if config else ['pension.toml', '~/.pension.toml']

    try:
        config = get_config(config_names)
    except:
        click.echo('Failed to parse config', err=True)
        return -1

    if config is None:
        click.echo('No usable config file, trying environment vars', err=True)
        config = {'notify': {'json': {}}}

    data = {'instances': [], 'profiles': {}}

    for prof, ec2_client in get_profiles(config).iteritems():
        statuses = get_instance_statuses(ec2_client, config)

        data['profiles'][prof] = [s['InstanceId'] for s in statuses]
        data['instances'].extend(statuses)

    click.echo('%d instance(s) have reported issues' % len(data['instances']),
               err=True)

    if dry_run:
        config['notify'] = {} if quiet else {'json': {}}

    notify.send(data, config['notify'])


if __name__ == '__main__':
    main()
