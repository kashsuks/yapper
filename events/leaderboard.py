import os
import sqlite3
import logging
from datetime import datetime, timezone
import requests
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DB_PATH = "leaderboard.db"
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

def initDb():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channelId TEXT NOT NULL,
            userId TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            UNIQUE(channelId, timestamp)
        )
    """)
    conn.commit()
    conn.close()

def insertMessage(channelId, userId, timestamp):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM messages WHERE channelId = ? AND timestamp = ?",
        (channelId, timestamp)
    )
    if not c.fetchone():
        c.execute(
            "INSERT INTO messages (channelId, userId, timestamp) VALUES (?, ?, ?)",
            (channelId, userId, timestamp)
        )
        conn.commit()
    conn.close()

def getCurrentMonthStartTs():
    now = datetime.now(timezone.utc)
    monthStart = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    return str(monthStart.timestamp())

def fetchMessagesFromSlack(channelId):
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    oldestTS = getCurrentMonthStartTs()
    messages = []
    cursor = None

    while True:
        params = {"channel": channelId, "oldest": oldestTS, "limit": 200}
        if cursor:
            params["cursor"] = cursor

        res = requests.get(
            "https://slack.com/api/conversations.history",
            headers=headers,
            params=params
        ).json()

        if not res.get("ok", False):
            logger.error(f"Error fetching messages: {res}")
            return

        messages.extend(res.get("messages", []))
        cursor = res.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    inserted = 0
    for msg in messages:
        user = msg.get("user")
        ts = msg.get("ts")
        if user:
            insertMessage(channelId, user, ts)
            inserted += 1

    logger.info(f"Fetched {len(messages)} messages from Slack, inserted {inserted} new messages into DB")

def getTopUsers(channelId, monthStartTS):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT userId, COUNT(*) as msgCount
        FROM messages
        WHERE channelId = ? AND timestamp >= ?
        GROUP BY userId
        ORDER BY msgCount DESC
        LIMIT 10
    """, (channelId, monthStartTS))
    results = c.fetchall()
    conn.close()
    return results

def register(app):
    initDb()

    @app.event("message")
    def handleMessageEvents(body, logger):
        try:
            event = body.get("event", {})
            user = event.get("user")
            channel = event.get("channel")
            if not user or event.get("subtype") == "bot_message":
                return
            insertMessage(channel, user, event.get("ts"))
        except Exception as e:
            logger.error(f"[leaderboard] Error handling message: {e}")

    @app.command("/yapperleaderboard")
    def yapperLeaderboard(ack, body, client, logger):
        ack()

        userId = body["userId"]
        channelId = body["channelId"]
        monthStartTS = getCurrentMonthStartTs()

        fetchMessagesFromSlack(channelId)

        topUsers = getTopUsers(channelId, monthStartTS)
        if not topUsers:
            client.chat_postEphemeral(
                channel=channelId,
                user=userId,
                text="No messages recorded yet this month in this channel."
            )
            return

        ldbLines = []
        for i, (uid, count) in enumerate(topUsers, 1):
            ldbLines.append(f"*{i}.* <@{uid}> — `{count}` messages")

        text = "*Yapper Leaderboard (Top 10 this month)*\n" + "\n".join(ldbLines)

        try:
            client.chat_postEphemeral(
                channel=channelId,
                user=userId,
                text=text
            )
            logger.info(f"[leaderboard] Sent leaderboard to {userId} in {channelId}")
        except SlackApiError as e:
            logger.error(f"[leaderboard] Slack error: {e.response['error']}")