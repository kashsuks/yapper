from slack_sdk import WebClient
from events.blacklist import blockIfBlacklisted

def register(app):
    @app.command("/yapperleave")
    @blockIfBlacklisted
    def leaveChannel(ack, body, client: WebClient, respond):
        ack()
        channelId = body["channel_id"]
        try:
            client.chat_postMessage(channel=channelId, text=f"👋 Leaving <#{channelId}> now. Bye!")
            client.conversations_leave(channel=channelId)
        except Exception as e:
            respond(f"⚠️ Error: {e}")