from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

# -------------------- ALL THE EVENT IMPORTS ------------------- #
from events import mention
from events import leetcode
from events import joined
from events import spotify
from events import osuSlack
from events import leave
from events import musicRoast

# event running
mention.register(app)
leetcode.register(app)
joined.register(app)
spotify.register(app)
osuSlack.register(app)
leave.register(app)
musicRoast.register(app)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()