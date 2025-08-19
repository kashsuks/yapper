from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os
import logging
from admin.server import run_admin_server_in_thread, SseLoggingHandler

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

# Event registering
mention.register(app)
leetcode.register(app)
joined.register(app)
spotify.register(app)
osuSlack.register(app)
leave.register(app)
musicRoast.register(app)

if __name__ == "__main__":
    # Configure root logger to INFO and attach SSE handler
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sse_handler = SseLoggingHandler()
    sse_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    sse_handler.setFormatter(formatter)
    logging.getLogger().addHandler(sse_handler)

    # Start admin server
    run_admin_server_in_thread()

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()