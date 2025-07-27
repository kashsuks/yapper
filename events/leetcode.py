import requests
from dotenv import load_dotenv
import os
import threading

load_dotenv()

lastKnownRating = {}

def extractRating(data: dict):
    userRank = data.get("userContestRanking")
    if userRank and "rating" in userRank:
        return int(userRank["rating"])
    return None

def fetchLeetCodeRating(handle: str):
    url = f"https://leetcode-api-pied.vercel.app/user/{handle}/contests"
    response = requests.get(url, timeout=5)
    data = response.json()
    return extractRating(data)

def startAutoRatingCheck(app):
    print("starting")
    handle = os.getenv("LEETCODE_HANDLE")
    slackUser = os.getenv("SLACK_USER_ID")
    channelId = os.getenv("SLACK_CHANNEL_ID", slackUser)  # fallback to DM if not specified

    def check():
        newRating = fetchLeetCodeRating(handle)
        if newRating is not None:
            prevRating = lastKnownRating.get(handle, newRating)
            delta = newRating - prevRating
            lastKnownRating[handle] = newRating

            if newRating != prevRating:
                emoji = "📈" if delta >= 0 else "📉"
                sign = "+" if delta >= 0 else ""
                app.client.chat_postMessage(
                    channel=channelId,
                    text=f"<@{slackUser}> {emoji} LeetCode rating update: `{prevRating}` → `{newRating}` ({sign}{delta})"
                )

        threading.Timer(60, check).start()

    check()  # run immediately

def register(app):
    startAutoRatingCheck(app)  # start background loop when bot registers