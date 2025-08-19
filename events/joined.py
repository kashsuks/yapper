from dotenv import load_dotenv
import os
import logging
from events.blacklist import blockIfBlacklisted

load_dotenv()
logger = logging.getLogger(__name__)

def register(app):
    @app.event("member_joined_channel")
    @blockIfBlacklisted
    def handleMemberJoinedChannelEvents(event, say, logger, body):
        user = event["user"]
        channel = event["channel"]
        try:
            message = f'Hi <@{user}>, welcome to the land where <@{os.getenv("SLACK_USER_ID")}> writes shit code'
            say(channel=channel, text=message)

            msg = f"Sent welcome message to <@{user}> in channel {channel}"
            logger.info(f"[joined] {msg}")

        except Exception as e:
            errorMsg = f"Failed to send welcome message to <@{user}> in channel {channel}: {e}"
            logger.error(f"[joined] {errorMsg}")