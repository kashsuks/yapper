import os
import requests
import random
import logging
import re
from slack_bolt import App
from events.blacklist import isBlacklisted

logger = logging.getLogger(__name__)

roastChannel = os.getenv("ROAST_CHANNEL_ID")
lastfmApiKey = os.getenv("LASTFM_API_KEY")

def getRecentTracks(user, limit=10):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": user,
        "api_key": lastfmApiKey,
        "format": "json",
        "limit": limit
    }
    try:
        logger.info(f"[musicRoast] Fetching recent tracks for {user}")

        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            errorMsg = f"Last.fm API returned status {resp.status_code} for user {user}"
            logger.error(f"[musicRoast] {errorMsg}")
            return []

        json_resp = resp.json()
        if 'error' in json_resp:
            errorMsg = f"Last.fm API error for user {user}: {json_resp['message']}"
            logger.error(f"[musicRoast] {errorMsg}")
            return []

        tracks = json_resp.get("recenttracks", {}).get("track", [])
        msg = f"Successfully fetched {len(tracks)} tracks for {user}"
        logger.info(f"[musicRoast] {msg}")
        return tracks

    except requests.exceptions.RequestException as e:
        errorMsg = f"Request exception for {user}: {e}"
        logger.error(f"[musicRoast] {errorMsg}")
        return []
    except Exception as e:
        errorMsg = f"Unknown exception for {user}: {e}"
        logger.error(f"[musicRoast] {errorMsg}")
        return []

def pickTrack(tracks):
    if not tracks:
        logger.warning("[musicRoast] No tracks provided to pickTrack()")
        return None

    track = random.choice(tracks)
    artist = track.get('artist', {}).get('#text', 'Unknown')
    name = track.get('name', 'Unknown')
    selected = f"{artist} - {name}"

    msg = f"Picked track {selected}"
    logger.info(f"[musicRoast] {msg}")

    return selected

def generateRoast(username, track, thread_ts=None):
    try:
        logger.info(f"[musicRoast] Generating roast for {username} with track {track}")

        response = requests.post(
            "https://ai.hackclub.com/chat/completions",
            headers={"Content-type": "application/json"},
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": f"Roast someone for listening to '{track}'. "
                                   f"Be funny, sarcastic, and a bit mean but not too harsh. "
                                   f"Keep it under 100 words. Don't use quotes around your response, just give me the roast directly."
                    }
                ]
            },
            timeout=15
        )

        if response.ok:
            ai_roast = response.json()["choices"][0]["message"]["content"].strip()
            ai_roast = re.sub(r"<think>.*?</think>", "", ai_roast, flags=re.DOTALL).strip()

            if (ai_roast.startswith('"') and ai_roast.endswith('"')) or \
               (ai_roast.startswith("'") and ai_roast.endswith("'")):
                ai_roast = ai_roast[1:-1].strip()

            roast = f"<@{username}> {ai_roast}"

            msg = f"Generated AI roast for {username}: {ai_roast}"
            logger.info(f"[musicRoast] {msg}")

            return roast
        else:
            fallback = f"yo <@{username}> really spinning *{track}*? that's wild 💀"
            errorMsg = f"AI API error (status {response.status_code}), using fallback for {username}"
            logger.error(f"[musicRoast] {errorMsg}")
            return fallback

    except Exception as e:
        fallback = f"yo <@{username}> really spinning *{track}*? that's questionable"
        errorMsg = f"Exception while generating roast for {username}: {e}"
        logger.error(f"[musicRoast] {errorMsg}")
        return fallback

def register(app: App):
    @app.event("message")
    def roastMessage(body, say):
        event = body.get("event", {})
        channel = event.get("channel")
        user = event.get("user")
        text = event.get("text", "").strip()
        subtype = event.get("subtype")
        message_ts = event.get("ts")
        thread_ts = event.get("thread_ts") or message_ts

        if channel != roastChannel:
            return

        if subtype == "bot_message" or not user:
            return

        if isBlacklisted(user):
            msg = f"User {user} is blacklisted, ignoring request"
            logger.warning(f"[musicRoast] {msg}")
            return

        if not text:
            say("Please provide your Last.fm username to get roasted!", thread_ts=thread_ts)
            msg = f"User {user} sent empty text in roast channel"
            logger.warning(f"[musicRoast] {msg}")
            return

        logger.info(f"[musicRoast] Received roast request from {user} with username {text}")

        tracks = getRecentTracks(text, 10)
        if not tracks:
            error_msg = f"Couldn't find what **{text}** has been listening to. Make sure that's your correct Last.fm username!"
            say(error_msg, thread_ts=thread_ts)

            logMsg = f"No tracks found for username {text}, request by {user}"
            logger.error(f"[musicRoast] {logMsg}")
            return

        track = pickTrack(tracks)
        if track:
            roast = generateRoast(user, track, thread_ts)
            say(roast, thread_ts=thread_ts)

            msg = f"Sent roast to {user} for track {track}"
            logger.info(f"[musicRoast] {msg}")
        else:
            say("Something went wrong picking a track to roast", thread_ts=thread_ts)

            msg = f"Failed to pick a track for {user}"
            logger.error(f"[musicRoast] {msg}")