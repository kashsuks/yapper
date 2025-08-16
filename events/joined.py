from dotenv import load_dotenv
import os

load_dotenv()

def register(app):
    @app.event("member_joined_channel")
    def handle_member_joined_channel_events(body, logger, event, say):
        logger.info(body)
        user = event["user"]
        channel = event["channel"]
        say(
            channel=channel,
            text=f'Hi <@{user}>, welcome to the land where <@{os.getenv("SLACK_USER_ID")}> writes shit code'
        )