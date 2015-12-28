import os
import os.path

from boto3.session import Session
import click
import toml

import notify


def get_instance_statuses(config):
    profile_name = config['aws'].get('profile', 'default')

    session = Session(profile_name=profile_name)
    client = session.client('ec2')

    def _filter(filters):
        _statuses = []
        next_token = ''

        while True:
            res = client.describe_instance_status(
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
    statuses = set(
        _filter({'event.code': ['*']}) +
        _filter({'instance-status.status': ['impaired']}) +
        _filter({'instance-status.reachability': ['failed']}) +
        _filter({'system-status.status': ['impaired']}) +
        _filter({'system-status.reachability': ['failed']})
    )

    return list(statuses)


def get_config(config_file):
    config_locations = [config_file, 'pension.toml', '~/.pension.toml']

    for loc in config_locations:
        file_name = os.path.expanduser(loc)

        if os.path.exists(file_name):
            click.echo('using config %s' % file_name)

            with open(file_name) as fp:
                return toml.loads(fp.read())


@click.command()
@click.option('--dry-run', is_flag=True, help='Disables sending alerts')
@click.option('--config', required=False, help='Configuration file location')
@click.option('--quiet', '-q', is_flag=True, help='Disables default JSON output')
def main(dry_run, config, quiet):
    try:
        config = get_config(config or '')
    except:
        click.echo('Failed to parse config')
        return -1

    if config is None:
        click.echo('No config file found!')
        return -1

    statuses = get_instance_statuses(config)

    click.echo('%d instance(s) have reported issues' % len(statuses))

    if dry_run:
        config['notify'] = {} if quiet else {'json': {}}

    notify.send(statuses, config['notify'])


if __name__ == '__main__':
    main()
