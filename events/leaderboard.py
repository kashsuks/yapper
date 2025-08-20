import os
import time
from datetime import datetime
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)


def monthStartTs():
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    return str(time.mktime(start.timetuple()))


def fetchMsgs(chanId):
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    oldest = monthStartTs()
    msgs = []
    cursor = None

    while True:
        params = {"channel": chanId, "oldest": oldest, "limit": 200}
        if cursor:
            params["cursor"] = cursor

        res = requests.get(
            "https://slack.com/api/conversations.history",
            headers=headers,
            params=params,
        ).json()

        if not res.get("ok", False):
            print(f"Error: {res}")
            break

        msgs.extend(res.get("messages", []))
        cursor = res.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    return msgs


def buildLb(msgs):
    counts = {}
    for m in msgs:
        u = m.get("user")
        if u:
            counts[u] = counts.get(u, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)


def register(app: App):
    @app.command("/yapperleaderboard")
    def handleLb(ack, body, respond):
        ack()
        chanId = body.get("channel_id")
        msgs = fetchMsgs(chanId)
        lb = buildLb(msgs)[:10]

        if not lb:
            respond(":speech_balloon: no msgs this month")
            return

        text = ":speech_balloon: *Yapper Leaderboard (Top 10 this month)*\n"
        for i, (u, c) in enumerate(lb, start=1):
            text += f"{i}. <@{u}> — {c} msgs\n"

        respond(text)