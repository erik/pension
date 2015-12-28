# pension

> Plan for your instances' retirement.

## config

pension uses [toml](https://github.com/mojombo/toml) as its configuration
language. The config file can be specified on the command line via `--config`.
If not provided, pension will try `./pension.toml` and `~/.pension.toml`.

```toml
# (optional) profile names as configured in ~/.aws/credentials
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
