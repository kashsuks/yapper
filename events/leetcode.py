import requests
from dotenv import load_dotenv
import os
import threading
import logging
from events.blacklist import isBlacklisted

load_dotenv()

lastKnownRating = {}
logger = logging.getLogger(__name__)

def extractRating(data: dict):
    userRank = data.get("userContestRanking")
    if userRank and "rating" in userRank:
        rating = int(userRank["rating"])
        logger.debug(f"[leetcode] Extracted rating: {rating}")
        return rating
    logger.warning("[leetcode] No rating found in response data")
    return None

def fetchLeetCodeRating(handle: str):
    try:
        url = f"https://leetcode-api-pied.vercel.app/user/{handle}/contests"
        logger.info(f"[leetcode] Fetching rating for {handle} from {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        rating = extractRating(data)
        logger.info(f"[leetcode] Fetched rating for {handle}: {rating}")
        return rating
    except Exception as e:
        logger.error(f"[leetcode] Error fetching rating for {handle}: {e}")
        return None

def startAutoRatingCheck(app):
    handle = os.getenv("LEETCODE_HANDLE")
    slackUser = os.getenv("SLACK_USER_ID")
    slackChannels = os.getenv("SLACK_CHANNEL_IDS", "").split(",")

    logger.info("[leetcode] Starting auto rating check...")

    if not handle or not slackUser:
        logger.error("[leetcode] Missing required env variables")
        return

    CHECK_INTERVAL = 86400

    def check():
        try:
            logger.debug("[leetcode] Running scheduled LeetCode rating check")

            newRating = fetchLeetCodeRating(handle)
            if newRating is not None:
                if handle not in lastKnownRating:
                    lastKnownRating[handle] = newRating
                    msg = f"Initial rating for {handle}: {newRating}"
                    logger.info(f"[leetcode] {msg}")
                else:
                    prevRating = lastKnownRating[handle]
                    if newRating != prevRating:
                        delta = newRating - prevRating
                        lastKnownRating[handle] = newRating
                        emoji = "📈" if delta >= 0 else "📉"
                        sign = "+" if delta >= 0 else ""
                        msg = f"<@{slackUser}> {emoji} LeetCode rating update: {prevRating} → {newRating} ({sign}{delta})"
                        logger.info(f"[leetcode] Rating change detected: {msg}")

                        for channel in slackChannels:
                            if isBlacklisted(channel):
                                logger.warning(f"[leetcode] Skipped posting to blacklisted channel: {channel}")
                                continue
                            app.client.chat_postMessage(channel=channel, text=msg)
                            logger.info(f"[leetcode] Posted rating update to channel {channel}")

            threading.Timer(CHECK_INTERVAL, check).start()
            logger.debug("[leetcode] Scheduled next rating check")

        except Exception as e:
            logger.error(f"[leetcode] Error in check function: {e}")
            threading.Timer(CHECK_INTERVAL, check).start()
            logger.debug("[leetcode] Rescheduled next rating check after exception")

    check()

def register(app):
    logger.info("[leetcode] Registering LeetCode auto rating check module")
    startAutoRatingCheck(app)