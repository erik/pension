# pension

> Plan for your instances' retirement.

Pension checks for EC2 instance retirement (e.g. due to hardware failures) and
other maintenance events that could cause (or be the source of) issues down the
line. It is meant to be run periodically (in a cron or some such) and provide
some warning before bad things happen.

Currently, pension knows how to ping a slack channel or send an email when
something's broken. Additional notification methods are welcome contributions.
Otherwise, parsing the JSON output format should be flexible enough for any
internal notification tooling.

### usage

`pip install pension`

`pension [--dry-run] [--quiet] [--config path/to/pension.toml]`

### configuration

pension uses [toml](https://github.com/mojombo/toml) as its configuration
language. The config file can be specified on the command line via `--config`.
If not provided, pension will try `./pension.toml` and `~/.pension.toml`.

If no config file is available, pension will try to proceed using only AWS
environment variables and the JSON console output.

For more information on AWS credentials, refer to the
[boto3 documentation](http://boto3.readthedocs.org/en/latest/guide/configuration.html).

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
user_name = "Bad News Bot"

# Sends an email using SMTP
[notify.email]
# (required)
server = "smtp.gmail.com"
# (required) login user name
user_name = "foobar@gmail.com"
# (required)
password = "hunter2"
# (optional) defaults to the given user_name
sender = "foo@bar.baz"
# (required)
recipients = ["oh@no.com", "alerts@myco.pagerduty.com"]
# (required)
subject = "Maintenance events detected for ec2 instances!"

[notify.json]
# (optional) file to write to. if not provided, will dump to stdout
file = "output.json"
```
