from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os
import logging
from admin.server import adminServer, SseLoggingHandler

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
LEETCODE_HANDLE = os.getenv("LEETCODE_HANDLE")
SLACK_USER_ID = os.getenv("SLACK_USER_ID")
SLACK_CHANNEL_IDS = os.getenv("SLACK_CHANNEL_IDS")
LASTFM_USER = os.getenv("LASTFM_USER")
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
OSU_ID = os.getenv("OSU_ID")
OSU_V1_API = os.getenv("OSU_V1_API")
BLACKLISTED_CHANNEL_IDS = os.getenv("BLACKLISTED_CHANNEL_IDS")
ROAST_CHANNEL_ID = os.getenv("ROAST_CHANNEL_ID")
ADMIN_PORT = int(os.getenv("ADMIN_PORT", 1234))

# -------------------- ALL THE EVENT IMPORTS ------------------- #
from events import mention
from events import leetcode
from events import joined
from events import spotify
from events import osuSlack
from events import leave
from events import musicRoast
from events import leaderboard
from events import scoreSubmission

# Event registering
mention.register(app)
leetcode.register(app)
joined.register(app)
spotify.register(app)
osuSlack.register(app)
leave.register(app)
musicRoast.register(app)
leaderboard.register(app)
scoreSubmission.register(app)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sseHandler = SseLoggingHandler()
    sseHandler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    sseHandler.setFormatter(formatter)
    logging.getLogger().addHandler(sseHandler)

    # Start admin server
    adminServer()

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()