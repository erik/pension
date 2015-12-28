# pension

> Plan for your instances' retirement.

Pension checks for EC2 instance retirement (e.g. due to hardware failures) and
other maintenance events that could cause (or be the source of) issues down the
line. It is meant to be run periodically (in a cron or some such) and provide
some warning before bad things happen.

### usage

`pip install pension`

`pension [--dry-run] [--quiet] [--config path/to/pension.toml]`

### configuration

pension uses [toml](https://github.com/mojombo/toml) as its configuration
language. The config file can be specified on the command line via `--config`.
If not provided, pension will try `./pension.toml` and `~/.pension.toml`.

If no config file is available, pension will try to proceed using only AWS
environment variables and the JSON console output.

#### example `pension.toml`

```toml
# (optional) profile names as configured in ~/.aws/credentials, defaults to
#            using boto's AWS environment variables.
aws_profiles = ["dev", "prod"]

# Enable notification via a slack message using webhooks.
# Hooks can be setup here: https://my.slack.com/services/new/incoming-webhook/
[notify.slack]
# (required)
hook_url = "https://hooks.slack.com/..."
# (optional) defaults to channel configured with webhook
channel = "#general"
# (optional) defaults to name configured with webhook
username = "Bad News Bot"

[notify.email]
# (required)
sender = "foo@bar.baz"
# (required)
recipients = ["oh@no.com", "alerts@myco.pagerduty.com"]
# (optional)
subject = "Oh no!"

[notify.json]
# (optional) file to write to. if not provided, will dump to stdout
file = "output.json"
```
