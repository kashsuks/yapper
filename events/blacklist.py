import os
import time
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

blacklistCache = set()
lastLoaded = 0
envPath = os.getenv("ENV_PATH", ".env")

def loadBlacklist():
    global blacklistCache, lastLoaded
    load_dotenv(envPath, override=True)
    channels = os.getenv("BLACKLISTED_CHANNEL_IDS", "")
    blacklistCache = set(ch.strip() for ch in channels.split(",") if ch.strip())
    try:
        lastLoaded = os.path.getmtime(envPath)
    except FileNotFoundError:
        lastLoaded = time.time()

loadBlacklist()

def isBlacklisted(channelId: str) -> bool:
    global lastLoaded
    try:
        mtime = os.path.getmtime(envPath)
        if mtime != lastLoaded:
            loadBlacklist()
    except FileNotFoundError:
        pass
    return channelId in blacklistCache

def blockIfBlacklisted(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        event = kwargs.get("event") or (args[0] if args else None)
        channelId = None
        if isinstance(event, dict):
            channelId = event.get("channel")
        if channelId and isBlacklisted(channelId):
            return
        return func(*args, **kwargs)
    return wrapper