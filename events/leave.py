from slack_sdk import WebClient

def register(app):
    @app.command("/yapperleave")
    def leave_channel(ack, body, client: WebClient, respond):
        ack()

        channel_id = body["channel_id"]

        try:
            client.chat_postMessage(
                channel=channel_id,
                text=f"👋 Leaving <#{channel_id}> now. Bye!"
            )

            client.conversations_leave(channel=channel_id)

        except Exception as e:
            respond(f"⚠️ Error: {e}")