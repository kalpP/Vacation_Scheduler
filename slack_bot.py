import slack
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, json, request, Response
from slackeventsapi import SlackEventAdapter
from slack import WebClient

load_dotenv()

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

vacation_requests = {}
approved_vacations = {}

@app.route('/vacation', methods=['POST'])
def message_actions():
    if(request.form.get("channel_name") == "request-time-off" or request.form.get("channel_id") == "C01J9SR0YAD"):
        result = client.views_open(
            trigger_id=request.form.get('trigger_id'),
            view={
                "type": "modal",
                "title": {"type": "plain_text", "text": "Schedule A Vacation"},
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
            },
        )
    else:
        client.chat_postMessage(channel = request.form.get("channel_name"), text=":exclamation:Cannot request time off in this channel:exclamation:")
    return Response(), 200

@app.route('/interactive', methods=['POST'])
def test_message():
    data = json.loads(request.form["payload"])
    if(data.get("type") == "view_submission"):
        user = data.get("user")
        user_id = user.get("id")
        user_name = user.get("name")
        view = data.get("view")
        state = view.get("state")
        values = state.get("values")
        reason_of_leave = values.get("reason_of_leave")
        reason_for_leave = reason_of_leave.get("reason_for_leave")
        leave_reason = reason_for_leave.get("value")
        vacation_start_date = values.get("vacation_start_date")
        vacation_start_date_picker = vacation_start_date.get("vacation_start_date_picker")
        start_date = vacation_start_date_picker.get("selected_date")
        vacation_end_date = values.get("vacation_end_date")
        vacation_end_date_picker = vacation_start_date.get("vacation_end_date_picker")
        end_date = vacation_start_date_picker.get("selected_date")

        client.chat_postMessage(
            channel="#managers",
	        blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "You have a new request:\n*<fakeLink.toEmployeeProfile.com|Fred Enriquez - New vacation request>*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Reason:*\nComputer (laptop)"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Start Date:*\nComputer (laptop)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*End Date:*\nSubmitted Aut 10"
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
            user_id = data.get("user").get("id")
            username = data.get("user").get("username")
            user_name = data.get("user").get("name")
            # Delete the old response
            client.chat_delete(channel=channel_id, ts=message_ts)
            if(decision == "Approve"):
                client.chat_postMessage(channel="#hr", text=f"Leave Request for {user_name} has been approved")
            else:
                client.chat_postMessage(channel=user_id, text="Your leave request has been denied :cry:")
        except:
            print('Ignore this error')
    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)