# last fm code to get my last song

import os
import time
import requests
from slack_sdk.errors import SlackApiError
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

lastfmUser = os.getenv("LASTFM_USER")
lastfmApiKey = os.getenv("LASTFM_API_KEY")
slackChannel = os.getenv("SLACK_CHANNEL_ID")

pollInterval = 15
session = None

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

def startSession(track, client):
    text = f"<@{os.getenv('SLACK_USER_ID')}> just started a new listening session! 🎶"
    res = client.chat_postMessage(channel=slackChannel, text=text)
    return {
        "startTime": getUnixTimestamp(),
        "lastTime": getUnixTimestamp(),
        "threadTs": res["ts"],
        "lastTrack": track.get("name", "")
    }

def postTrackToThread(track, threadTs, client):
    name = track.get("name", "Unknown")
    artist = track.get("artist", {}).get("#text", "Unknown")
    text = f"*{artist}* – *{name}*"
    client.chat_postMessage(channel=slackChannel, text=text, thread_ts=threadTs)

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

                if session:
                    if getUnixTimestamp() - session["lastTime"] > 1800:
                        session = None
                    elif trackName != session["lastTrack"]:
                        postTrackToThread(track, session["threadTs"], client)
                        session["lastTrack"] = trackName
                        session["lastTime"] = getUnixTimestamp()
                elif nowPlaying:
                    session = startSession(track, client)
                    postTrackToThread(track, session["threadTs"], client)
            except SlackApiError as e:
                print(f"Slack error: {e.response['error']}")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(pollInterval)

    from threading import Thread
    Thread(target=runPolling, daemon=True).start()