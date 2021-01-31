# Vacation Scheduler
A Slack bot for scheduling/managing vacations


**Instructions**:

1.) Visit: https://api.slack.com/   
2.) Click "Start Building"  
3.) Fill in the request information  
	* Make sure you are saving changes as you follow these next steps  
4.) In 'Basic Information' under 'Settings' you can scroll all the way down to change the bot icon/name/description  
5.) Go to 'OAuth & Permissions' under 'Features'. Then scoll down to the 'Scopes' section and add an OAuth scope for:  
	channels:history   
	chat:write   
	commands   
6.) Create a '.env' file in the same directory as the file 'slack_bot.py'   
7.) In the same section, you will find a 'Bot User OAuth Access Token'. Copy and paste that into a '.env' file:   
	SLACK_TOKEN = <your token>   
8.) Go to 'Basic Information' under 'Settings', click show next to the 'Signing Secret'. Copy and paste this into the '.env' file:   
	SIGNING_SECRET = <your signing secret>   
9.) In the same section, click 'Install your app' into the workspace. Allow the requested access.   
10.) Download and run the ngrok.exe file. In the file type in the command:   
	ngrok http 5000   
	* Save ngrok.exe in the same folder as your '.env' and 'slack_bot.py' files   
	* If you want to change the port number you cann replace it for the '5000' in the command and also make the changes in slack_bot.py file   
	* Download link: https://ngrok.com/download   
11.) After doing that you will get a forwarding address, you can use either the http or the https one. Copy the address   
	Ex: https://88e623ac2d58.ngrok.io   
12.) Run the slack_bot.py file   
13.) Go back to https://api.slack.com/   
14.) Then go to 'Event Subscriptions' under 'Features'   
15.) In the 'Request URL' field type in the forwarding address you copied, followed by "/slack/events"   
	Ex: https://88e623ac2d58.ngrok.io/slack/events   
	After you type this in, you should see a green 'Verified' checkmark above the text-field. If not, try repeating steps 8-10   
16.) Go to 'Interactivity & Shortcuts' under 'Features'   
17.) In the 'Request URL' field type in the forwarding address you copied, followed by "/interactive"   
	Ex: https://88e623ac2d58.ngrok.io/interactive   
18.) Go to 'Slash Commands' under 'Features'   
19.) Click 'Create New Command'   
20.) Fill in the information:   
	In the 'Command' field type in: "/vacation"   
	In the 'Request URL' type in: "https://88e623ac2d58.ngrok.io/vacations"   
	In the 'Short Description' you can type in anything   
21.) You might have to reinstall the app into your workspace, you will know you have to reinstall it if you see a yellow bar on top telling you to do so.   
