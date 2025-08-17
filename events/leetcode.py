import requests
from dotenv import load_dotenv
import os
import threading
import logging
from events.blacklist import isBlacklisted, blockIfBlacklisted

load_dotenv()

lastKnownRating = {}
logger = logging.getLogger(__name__)

def extractRating(data: dict):
    userRank = data.get("userContestRanking")
    if userRank and "rating" in userRank:
        return int(userRank["rating"])
    return None

def fetchLeetCodeRating(handle: str):
    try:
        url = f"https://leetcode-api-pied.vercel.app/user/{handle}/contests"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return extractRating(data)
    except Exception as e:
        logger.error(f"Error fetching rating for {handle}: {e}")
        return None

def startAutoRatingCheck(app):
    handle = os.getenv("LEETCODE_HANDLE")
    slackUser = os.getenv("SLACK_USER_ID")
    slackChannels = os.getenv("SLACK_CHANNEL_IDS", "").split(",")
    if not handle or not slackUser:
        logger.error("Missing required env variables")
        return
    CHECK_INTERVAL = 86400

    def check():
        try:
            newRating = fetchLeetCodeRating(handle)
            if newRating is not None:
                if handle not in lastKnownRating:
                    lastKnownRating[handle] = newRating
                    logger.info(f"Initial rating for {handle}: {newRating}")
                else:
                    prevRating = lastKnownRating[handle]
                    if newRating != prevRating:
                        delta = newRating - prevRating
                        lastKnownRating[handle] = newRating
                        emoji = "📈" if delta >= 0 else "📉"
                        sign = "+" if delta >= 0 else ""
                        for channel in slackChannels:
                            if isBlacklisted(channel):
                                continue
                            app.client.chat_postMessage(
                                channel=channel,
                                text=f"<@{slackUser}> {emoji} LeetCode rating update: {prevRating} → {newRating} ({sign}{delta})"
                            )
            threading.Timer(CHECK_INTERVAL, check).start()
        except Exception as e:
            logger.error(f"Error in check function: {e}")
            threading.Timer(CHECK_INTERVAL, check).start()

    check()

def register(app):
    startAutoRatingCheck(app)