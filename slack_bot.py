import slack
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, json, request, Response
from slackeventsapi import SlackEventAdapter
from slack import WebClient
from random import randint

load_dotenv()

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

month_dict = {"01":"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August","09":"September","10":"October","11":"November","12":"December"}

# No parameters sent: ERROR = {'ok': False, 'error': 'not_allowed_token_type'}
# Only takes 1 argument: https://api.slack.com/methods/admin.emoji.add
@app.route('/add-emoji', methods=['GET', 'POST'])
def add_emoji():
    name = (request.form.get("text")).split(', ')[0]
    url = (request.form.get("text")).split(', ')[1]
    client.admin_emoji_add()
    return Response(), 200

@app.route('/coin-flip', methods=['POST'])
def coin_flip():
    tests = (request.form.get("text")).replace(" ", "")
    results = []
    try:
        tests = int(tests)
    except:
        tests = 1
    
    for test in range(tests):
        results.append("Head" if(randint(1,1000) % 2 == 0) else "Tail")
    flip_result = ''
    heads_counter, tails_counter = 0, 0
    for result in results:
        if(result == "Head"):
            heads_counter += 1
        else:
            tails_counter += 1
    
    if(heads_counter == tails_counter):
        flip_result = "Heads" if(randint(1,100) % 2 == 0) else "Tails"
    elif(heads_counter > tails_counter):
        flip_result = "Head"
    else:
        flip_result = "Tail"
    client.chat_postMessage(channel=request.form.get("channel_name"), text=flip_result)

    return Response(), 200

@app.route('/request-leave', methods=['POST'])
def message_actions():
    if(request.form.get("channel_name") == "request-time-off"):
        result = client.views_open(
            trigger_id=request.form.get('trigger_id'),
            view={
                "type": "modal",
                "title": {"type": "plain_text", "text": "Request a leave"},
                "close": {"type": "plain_text", "text": "Close"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "reason_of_leave",
                        "label": {
                            "type": "plain_text",
                            "text": "Reason for leave",
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "reason_for_leave",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Enter reason here..."
                            }
                        }
                    },
                    {
                        "type": "section",
                        "block_id": "vacation_start_date",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Pick the start date:"
                        },
                        "accessory": {
                            "type": "datepicker",
                            "action_id": "vacation_start_date_picker",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select a date"
                            }
                        }
                    },
                    {
                        "type": "section",
                        "block_id": "vacation_end_date",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Pick the end date:"
                        },
                        "accessory": {
                            "type": "datepicker",
                            "action_id": "vacation_end_date_picker",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select a date"
                            }
                        }
                    }
                ],
            }
        )
        return Response(), 200
    else:
        client.chat_postMessage(channel = request.form.get("channel_name"), text=":exclamation:Cannot request time off in this channel:exclamation:")
    return Response(), 200

@app.route('/interactive', methods=['POST'])
def test_message():
    workspace_domain = f"https://{client.team_info().get('team').get('domain')}.slack.com/team/"
    data = json.loads(request.form["payload"])
    if(data.get("type") == "view_submission"):
        user = data.get("user")
        user_id = user.get("id")
        user_name = user.get("name")
        user_profile_url = workspace_domain + user_id

        values = data.get("view").get("state").get("values")
        reason_of_leave = values.get("reason_of_leave").get("reason_for_leave").get("value")
        start_date = values.get("vacation_start_date").get("vacation_start_date_picker").get("selected_date").split('-')
        end_date = values.get("vacation_end_date").get("vacation_end_date_picker").get("selected_date").split('-')

        client.chat_postMessage(
            channel="#managers",
	        blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"You have a new request:\n*<{user_profile_url}|{user_name} - New vacation request>*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Reason:*\n{reason_of_leave}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Start Date:*\n{month_dict[start_date[1]]} {start_date[2]}, {start_date[0]}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*End Date:*\n{month_dict[end_date[1]]} {end_date[2]}, {end_date[0]}"
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Approve"
                            },
                            "style": "primary",
                            "value": "click_me_123"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Deny"
                            },
                            "style": "danger",
                            "value": "click_me_123"
                        }
                    ]
                }
	        ]
        )
    elif(data.get("type") == "block_actions"):
        try:
            # Get Response
            container = data.get("container")
            message_ts = container.get("message_ts")
            channel_id = container.get("channel_id")
            decision = data.get("actions")[0].get("text").get("text")
            # Manager info
            manager_user_id = data.get('user').get('id')
            manager_username = data.get('user').get('username')
            manager_name = data.get('user').get('name')
            # User info
            temp = data.get('message').get('blocks')[0].get('text').get('text')
            user_id = temp[temp.index('/U') + 1 : temp.index('|')]
            user_info = client.users_info(user = user_id)
            username = user_info.get("user").get("name")
            user_name = user_info.get("user").get("real_name")
            # Delete responded message
            client.chat_delete(channel=channel_id, ts=message_ts)
            if(decision == "Approve"):
                client.chat_postMessage(channel="#hr", text=f"Leave Request for {user_name} has been approved by {manager_name}")
                client.chat_postMessage(channel=user_id, text="Your leave request has been approved :smiley:")
                return Response(), 200
            else:
                client.chat_postMessage(channel=user_id, text="Your leave request has been denied :cry:")
                return Response(), 200
        except:
            print('Ignore this error')
    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)