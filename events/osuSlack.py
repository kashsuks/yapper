import os
import time
import threading
from dotenv import load_dotenv
from osu import Client, UserScoreType
from slack_sdk import WebClient
from events.blacklist import isBlacklisted, blockIfBlacklisted

load_dotenv()

id = int(os.getenv("CLIENT_ID"))
secret = os.getenv("CLIENT_SECRET")
osuId = os.getenv("OSU_ID")
slackToken = os.getenv("SLACK_BOT_TOKEN")
slackChannels = os.getenv("SLACK_CHANNEL_IDS", "").split(",")

osuClient = Client.from_credentials(id, secret, None)
slackClient = WebClient(token=slackToken)

def formatScore(score):
    beatmap = score.beatmapset
    url = f"https://osu.ppy.sh/beatmapsets/{beatmap.id}#{score.beatmap.mode.value}/{score.beatmap.id}"
    return f"*{beatmap.artist}* – *{beatmap.title}* [{score.beatmap.version}]\n{round(score.pp or 0, 2)}pp | {score.accuracy * 100:.2f}% | Rank: {score.rank} | <{url}|Beatmap Link>"

def postMessageToChannels(msg, threadTs=None):
    for channel in slackChannels:
        if isBlacklisted(channel):
            continue
        slackClient.chat_postMessage(channel=channel, text=msg, thread_ts=threadTs)

def loop():
    lastScore = None
    threadTs = None
    while True:
        try:
            scores = osuClient.get_user_scores(osuId, UserScoreType.RECENT, limit=1)
            if scores:
                score = scores[0]
                currScore = f"{score.beatmapset.id}-{score.ended_at}"
                if currScore != lastScore:
                    lastScore = currScore
                    msg = formatScore(score)
                    if threadTs is None:
                        for channel in slackChannels:
                            if isBlacklisted(channel):
                                continue
                            resp = slackClient.chat_postMessage(channel=channel, text="osu! session started! (watch him miss everything)")
                            threadTs = resp["ts"]
                            break
                    postMessageToChannels(msg, threadTs)
            time.sleep(10)
        except Exception as e:
            print(f"[osu] error: {e}")
            time.sleep(60)

def register(app):
    threading.Thread(target=loop, daemon=True).start()