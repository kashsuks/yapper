import os
import time
import requests
import logging
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from events.blacklist import isBlacklisted

load_dotenv()

lastfmUser = os.getenv("LASTFM_USER")
lastfmApiKey = os.getenv("LASTFM_API_KEY")
slackChannels = os.getenv("SLACK_CHANNEL_IDS", "").split(",")
pollInterval = 15
session = None
logger = logging.getLogger(__name__)


def getRecentTrack():
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": lastfmUser,
        "api_key": lastfmApiKey,
        "format": "json",
        "limit": 1
    }
    res = requests.get(url, params=params).json()
    return res.get("recenttracks", {}).get("track", [])[0]


def getUnixTimestamp():
    return int(time.time())


def parseTimestamp(track):
    if "date" in track:
        return int(track["date"]["uts"])
    return getUnixTimestamp()


def startSession(track, client, channel):
    text = f"<@{os.getenv('SLACK_USER_ID')}> just started a new listening session (he is peak unemployed)"
    res = client.chat_postMessage(channel=channel, text=text)
    msg = f"Started new session in {channel} with track: {track.get('name', 'Unknown')}"
    logger.info(f"[lastfm] {msg}")
    return {
        "startTime": getUnixTimestamp(),
        "lastTime": getUnixTimestamp(),
        "threadTs": res["ts"],
        "lastTrack": track.get("name", "")
    }


def postTrack(track, threadTs, client, channel):
    name = track.get("name", "Unknown")
    artist = track.get("artist", {}).get("#text", "Unknown")
    url = track.get("url", "").strip('"')
    text = f"*{artist}* – <{url}|{name}>"
    client.chat_postMessage(channel=channel, text=text, thread_ts=threadTs)
    msg = f"Posted track in {channel}: {artist} – {name}"
    logger.info(f"[lastfm] {msg}")


def register(app):
    client = app.client
    global session

    def runPolling():
        global session
        while True:
            try:
                track = getRecentTrack()
                if not track:
                    time.sleep(pollInterval)
                    continue

                nowPlaying = track.get("@attr", {}).get("nowplaying") == "true"
                trackName = track.get("name")
                ts = parseTimestamp(track)

                for channel in slackChannels:
                    if isBlacklisted(channel):
                        logger.info(f"[lastfm] skipped blacklisted channel {channel}")
                        continue

                    if session:
                        if getUnixTimestamp() - session["lastTime"] > 1800:
                            logger.info("[lastfm] session expired due to inactivity")
                            session = None
                        elif trackName != session["lastTrack"]:
                            postTrack(track, session["threadTs"], client, channel)
                            session["lastTrack"] = trackName
                            session["lastTime"] = getUnixTimestamp()
                    elif nowPlaying:
                        session = startSession(track, client, channel)
                        postTrack(track, session["threadTs"], client, channel)

            except SlackApiError as e:
                errorMsg = f"Slack error: {e.response['error']}"
                logger.error(f"[lastfm] {errorMsg}")
            except Exception as e:
                errorMsg = f"Error: {e}"
                logger.error(f"[lastfm] {errorMsg}")

            time.sleep(pollInterval)

    from threading import Thread
    Thread(target=runPolling, daemon=True).start()