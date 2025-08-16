import requests
from dotenv import load_dotenv
import os
import threading
import time
import logging

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
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        return extractRating(data)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching rating for {handle}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def startAutoRatingCheck(app):
    print("Starting LeetCode rating checker...")
    handle = os.getenv("LEETCODE_HANDLE")
    slackUser = os.getenv("SLACK_USER_ID")
    channelId = os.getenv("SLACK_CHANNEL_ID", slackUser)
    
    if not handle or not slackUser:
        logger.error("Missing required environment variables: LEETCODE_HANDLE and SLACK_USER_ID")
        return
    
    CHECK_INTERVAL = 86400
    
    def check():
        try:
            print("checking")
            newRating = fetchLeetCodeRating(handle)
            print(f"Current rating: {newRating}")
            
            if newRating is not None:
                # init if its first time
                if handle not in lastKnownRating:
                    lastKnownRating[handle] = newRating
                    print(f"Initial rating set for {handle}: {newRating}")
                    logger.info(f"Initial rating for {handle}: {newRating}")
                else:
                    prevRating = lastKnownRating[handle]
                    print(f"Previous: {prevRating}, Current: {newRating}")
                    
                    if True:
                        print("im here")
                        delta = newRating - prevRating
                        lastKnownRating[handle] = newRating
                        
                        emoji = "📈" if delta >= 0 else "📉"
                        sign = "+" if delta >= 0 else ""
                        
                        try:
                            print("Sending Slack message...")
                            response = app.client.chat_postMessage(
                                channel=channelId,
                                text=f"<@{slackUser}> {emoji} LeetCode rating update: `{prevRating}` → `{newRating}` ({sign}{delta})"
                            )
                            print(f"Slack message sent successfully! Response: {response}")
                            logger.info(f"Rating update sent: {prevRating} → {newRating}")
                        except Exception as e:
                            print(f"Slack error: {e}")
                            logger.error(f"Error sending Slack message: {e}")
                    else:
                        print("No rating change detected")
            else:
                print("Failed to fetch rating")
                logger.warning(f"Could not fetch rating for {handle}")
                
        except Exception as e:
            print(f"Check function error: {e}")
            logger.error(f"Error in check function: {e}")
        
        threading.Timer(CHECK_INTERVAL, check).start()
    
    check()

def register(app):
    startAutoRatingCheck(app)