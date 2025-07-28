import os
import time
import requests
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()

lastfmUser = os.getenv("LASTFM_USER")
lastfmApiKey = os.getenv("LASTFM_API_KEY")
slackChannels = os.getenv("SLACK_CHANNEL_IDS", "").split(",")
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
    text = f"<@{os.getenv('SLACK_USER_ID')}> just started a new listening session (he is peak unemployed)"
    threadTsMap = {}
    for channel in slackChannels:
        res = client.chat_postMessage(channel=channel.strip(), text=text)
        threadTsMap[channel.strip()] = res["ts"]
    return {
        "startTime": getUnixTimestamp(),
        "lastTime": getUnixTimestamp(),
        "threadTsMap": threadTsMap,
        "lastTrack": track.get("name", "")
    }

def postTrack(track, threadTsMap, client):
    name = track.get("name", "Unknown")
    artist = track.get("artist", {}).get("#text", "Unknown")
    url = track.get("url", "").strip('"')
    text = f"*{artist}* – <{url}|{name}>"
    for channel, threadTs in threadTsMap.items():
        client.chat_postMessage(channel=channel, text=text, thread_ts=threadTs)

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
                        postTrack(track, session["threadTsMap"], client)
                        session["lastTrack"] = trackName
                        session["lastTime"] = getUnixTimestamp()
                elif nowPlaying:
                    session = startSession(track, client)
                    postTrack(track, session["threadTsMap"], client)
            except SlackApiError as e:
                print(f"Slack error: {e.response['error']}")
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(pollInterval)

    from threading import Thread
    Thread(target=runPolling, daemon=True).start()