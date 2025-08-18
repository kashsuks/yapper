import os
import requests
import random
import logging
import re
from slack_bolt import App
from events.blacklist import isBlacklisted

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
        resp = requests.get(url, params=params, timeout=10)
        
        if resp.status_code != 200:
            return []
            
        json_resp = resp.json()
        
        if 'error' in json_resp:
            return []
        
        tracks = json_resp.get("recenttracks", {}).get("track", [])
        return tracks
        
    except requests.exceptions.RequestException as e:
        return []
    except Exception as e:
        return []

def pickTrack(tracks):
    if not tracks:
        return None
    
    track = random.choice(tracks)
    artist = track.get('artist', {}).get('#text', 'Unknown')
    name = track.get('name', 'Unknown')
    selected = f"{artist} - {name}"
    return selected

def generateRoast(username, track, thread_ts=None):
    try:
        response = requests.post(
            "https://ai.hackclub.com/chat/completions",
            headers={"Content-type": "application/json"},
            json={
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Roast someone for listening to '{track}'. Be funny, sarcastic, and a bit mean but not too harsh. Keep it under 100 words. Don't use quotes around your response, just give me the roast directly."
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
            return roast
        else:
            fallback = f"yo <@{username}> really spinning *{track}*? that's wild 💀"
            return fallback
            
    except Exception as e:
        fallback = f"yo <@{username}> really spinning *{track}*? that's questionable"
        return fallback

def register(app: App):
    @app.event("message")
    def roastMessage(body, say, logger):
        event = body.get("event", {})
        channel = event.get("channel")
        user = event.get("user")
        text = event.get("text", "").strip()
        subtype = event.get("subtype")
        message_ts = event.get("ts")
        thread_ts = event.get("thread_ts") or message_ts

        # 🚨 only allow in roastChannel
        if channel != roastChannel:
            return

        if subtype == "bot_message" or not user:
            return

        if not text:
            say("Please provide your Last.fm username to get roasted!", thread_ts=thread_ts)
            return

        tracks = getRecentTracks(text, 10)
        if not tracks:
            error_msg = f"couldn't find what **{text}** has been listening to. Make sure that's your correct Last.fm username!"
            say(error_msg, thread_ts=thread_ts)
            return

        track = pickTrack(tracks)
        if track:
            roast = generateRoast(user, track, thread_ts)
            say(roast, thread_ts=thread_ts)
        else:
            say("Something went wrong picking a track to roast", thread_ts=thread_ts)