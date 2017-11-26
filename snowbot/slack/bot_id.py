import os
from slackclient import SlackClient

SLACK_BOT_NAME = 'snowbot'
SLACK_BOT_TOKEN_ENV_NAME = 'SLACK_BOT_TOKEN'


def bot_id():
    token = os.environ.get(SLACK_BOT_TOKEN_ENV_NAME)
    if not token:
        print('must set token in env variable' + SLACK_BOT_TOKEN_ENV_NAME)
    client = SlackClient(token)
    list_users = client.api_call('users.list')
    if list_users.get('ok'):
        users = list_users.get('members')
        print('total {} users'.format(len(users)))
        for user in users:
            if user.get('name') == SLACK_BOT_NAME:
                return user.get('id')
    else:
        return ''


if __name__ == '__main__':
    print('{} id is {}'.format(SLACK_BOT_NAME, bot_id()))
