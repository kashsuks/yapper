import os
import time
import threading
import logging
from typing import Optional
from dotenv import load_dotenv
from osu import Client, UserScoreType, score
from slack_sdk import WebClient
from events.blacklist import isBlacklisted

load_dotenv()

CLIENT_ID = int(os.getenv("CLIENT_ID", "0"))
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
OSU_ID = os.getenv("OSU_ID", "")
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNELS = [c.strip() for c in os.getenv("SLACK_CHANNEL_IDS", "").split(",") if c.strip()]

osuClient = Client.from_credentials(CLIENT_ID, CLIENT_SECRET, None)
slackClient = WebClient(token=SLACK_TOKEN)

logger = logging.getLogger(__name__)

def logMessage(level: str, msg: str):
    formatted = f"[osuSlack] {msg}"
    if level == "info":
        logger.info(formatted)
    elif level == "error":
        logger.error(formatted)
    else:
        logger.debug(formatted)

def formatScore(score: score) -> str:
    beatmap = score.beatmapset
    url = f"https://osu.ppy.sh/beatmapsets/{beatmap.id}#{score.beatmap.mode.value}/{score.beatmap.id}"
    return (
        f"*{beatmap.artist}* – *{beatmap.title}* [{score.beatmap.version}]\n"
        f"{round(score.pp or 0, 2)}pp | {score.accuracy * 100:.2f}% | "
        f"Rank: {score.rank} | <{url}|Beatmap Link>"
    )

def postMessageToChannels(msg: str, threadTs: Optional[str] = None):
    for channel in SLACK_CHANNELS:
        if isBlacklisted(channel):
            logMessage("info", f"skipped blacklisted channel {channel}")
            continue
        try:
            slackClient.chat_postMessage(channel=channel, text=msg, thread_ts=threadTs)
            logMessage("info", f"posted message to channel {channel} (thread={threadTs})")
        except Exception as e:
            logMessage("error", f"error posting to {channel}: {e}")

def loop():
    lastScore: Optional[str] = None
    threadTs: Optional[str] = None
    logMessage("info", "loop started")

    while True:
        try:
            scores = osuClient.get_user_scores(OSU_ID, UserScoreType.RECENT, limit=1)
            if scores:
                score = scores[0]
                currScore = f"{score.beatmapset.id}-{score.ended_at}"

                if currScore != lastScore:
                    lastScore = currScore
                    msg = formatScore(score)

                    if threadTs is None:
                        for channel in SLACK_CHANNELS:
                            if isBlacklisted(channel):
                                logMessage("info", f"skipped blacklisted channel {channel}")
                                continue
                            try:
                                resp = slackClient.chat_postMessage(
                                    channel=channel,
                                    text="osu! session started! (watch him miss everything)"
                                )
                                threadTs = resp.get("ts")
                                logMessage("info", f"created new session thread in {channel} (ts={threadTs})")
                                break
                            except Exception as e:
                                logMessage("error", f"failed to create thread in {channel}: {e}")

                    postMessageToChannels(msg, threadTs)

            time.sleep(10)

        except Exception as e:
            logMessage("error", f"error in loop: {e}")
            time.sleep(60)

def register(app):
    threading.Thread(target=loop, daemon=True).start()
    logMessage("info", "registered background thread")