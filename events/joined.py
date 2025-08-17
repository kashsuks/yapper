from dotenv import load_dotenv
import os
from events.blacklist import blockIfBlacklisted

load_dotenv()

def register(app):
    @app.event("member_joined_channel")
    @blockIfBlacklisted
    def handleMemberJoinedChannelEvents(event, say, logger, body):
        user = event["user"]
        channel = event["channel"]
        say(channel=channel, text=f'Hi <@{user}>, welcome to the land where <@{os.getenv("SLACK_USER_ID")}> writes shit code')