# Slack Integration

- [#3](https://github.com/at15/snowbot/issues/3)

````bash
virtualenv env
source env/bin/activate
````

- change settings in pycharm to make use of virtualenv in `Project Interpreter`
- create bot using https://my.slack.com/services/new/bot

````bash
export SLACK_BOT_TOKEN=your-token
python snowbot/slack/bot_id.py
````