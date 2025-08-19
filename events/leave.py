import logging
from slack_sdk import WebClient
from events.blacklist import blockIfBlacklisted

logger = logging.getLogger(__name__)

def register(app):
    @app.command("/yapperleave")
    @blockIfBlacklisted
    def leaveChannel(ack, body, client: WebClient, respond):
        ack()
        channelId = body["channel_id"]
        try:
            client.chat_postMessage(channel=channelId, text=f"👋 Leaving <#{channelId}> now. Bye!")
            client.conversations_leave(channel=channelId)

            msg = f"Bot left channel {channelId}"
            logger.info(f"[leave] {msg}")

        except Exception as e:
            errorMsg = f"Failed to leave channel {channelId}: {e}"
            logger.error(f"[leave] {errorMsg}")
            respond(f"⚠️ Error: {e}")