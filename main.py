from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

# basic handling
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

@app.event("app_mention")
def mention(event, say):
    user = event["user"]
    threadTs = event.get("thread_ts") or event["ts"]
    say(f"What the fuck do you want <@{user}>", thread_ts = threadTs)
    
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()