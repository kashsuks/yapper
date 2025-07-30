import os
import time
import threading
from dotenv import load_dotenv
from osu import Client, UserScoreType
from slack_sdk import WebClient

load_dotenv()

id = int(os.getenv("id"))
secret = os.getenv("secret")
osuId = os.getenv("OSU_ID")
slackToken = os.getenv("SLACK_BOT_TOKEN")
slackChannel = os.getenv("slackChannel_ID")

osuClient = Client.from_credentials(id, secret, None)
slackClient = WebClient(token=slackToken)


def formatScore(score):
    beatmap = score.beatmapset
    url = f"https://osu.ppy.sh/beatmapsets/{beatmap.id}#{score.beatmap.mode.value}/{score.beatmap.id}"
    return (
        f"*{beatmap.artist}* – *{beatmap.title}* [{score.beatmap.version}]\n"
        f"{round(score.pp or 0, 2)}pp | {score.accuracy * 100:.2f}% | Rank: {score.rank} | [Beatmap Link]({url})"
    )


def loop():
    lastScore = None
    thread_ts = None

    while True:
        try:
            scores = osuClient.get_user_scores(osuId, UserScoreType.RECENT, limit=1)
            if scores:
                score = scores[0]
                currScore = f"{score.beatmapset.id}-{score.ended_at}"

                if currScore != lastScore:
                    lastScore = currScore
                    msg = formatScore(score)

                    if thread_ts is None:
                        resp = slackClient.chat_postMessage(channel=slackChannel, text="🎮 osu! session started!")
                        thread_ts = resp["ts"]

                    slackClient.chat_postMessage(channel=slackChannel, text=msg, thread_ts=thread_ts)

            time.sleep(30)

        except Exception as e:
            print(f"[osu] error: {e}")
            time.sleep(60)


def register(app):
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()