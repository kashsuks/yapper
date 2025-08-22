import requests
import re
import logging
import os
from events.blacklist import blockIfBlacklisted

logger = logging.getLogger(__name__)

def getBlacklist():
    return [uid.strip() for uid in os.getenv("MENTION_BLACKLIST", "").split(",") if uid.strip()]

def register(app):
    @app.event("app_mention")
    @blockIfBlacklisted
    def mention(event, say):
        userId = event["user"]
        fullText = event.get("text", "")
        threadTs = event.get("thread_ts") or event["ts"]
        botUserId = app.client.auth_test()["user_id"]
        strippedText = fullText.replace(f"<@{botUserId}>", "").strip()

        mentionedIds = re.findall(r"<@([A-Z0-9]+)>", fullText)

        blacklistUserIds = getBlacklist()
        if any(uid in blacklistUserIds for uid in mentionedIds if uid != botUserId):
            logger.info(f"[mention] Ignored because blacklisted user mentioned: {mentionedIds}")
            return
        # ---------------------------------------------------------------

        msg = f"Mention received from <@{userId}>: {strippedText}"
        logger.info(f"[mention] {msg}")

        if strippedText == "":
            msg = f"What the f**k is your problem <@{userId}>"
            say(msg, thread_ts=threadTs)

            logMsg = f"Responded to empty mention for <@{userId}>: {msg}"
            logger.info(f"[mention] {logMsg}")
            return

        try:
            logMsg = f"Sending AI request for <@{userId}> with text: {strippedText}"
            logger.info(f"[mention] {logMsg}")

            response = requests.post(
                "https://ai.hackclub.com/chat/completions",
                headers={"Content-type": "application/json"},
                json={
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Give me a bitchy and annoying karen like response. Only return the final response, not anything between <think> tags: {strippedText}"
                        }
                    ]
                },
                timeout=10
            )

            if response.ok:
                logger.info(f"[mention] AI request successful for <@{userId}>")

                aiReply = response.json()["choices"][0]["message"]["content"]
                filteredReply = re.sub(r"<think>.*?</think>", "", aiReply, flags=re.DOTALL).strip()

                if (filteredReply.startswith('"') and filteredReply.endswith('"')) or \
                   (filteredReply.startswith("'") and filteredReply.endswith("'")):
                    filteredReply = filteredReply[1:-1].strip()

                say(filteredReply, thread_ts=threadTs)

                msg = f"Sent AI reply to <@{userId}>: {filteredReply}"
                logger.info(f"[mention] {msg}")

            else:
                errorMsg = f"AI API error for <@{userId}>. Response: {response.text}"
                logger.error(f"[mention] {errorMsg}")

                fallbackMsg = "Shut up, even the AI doesn't want to respond to that."
                say(fallbackMsg, thread_ts=threadTs)

        except Exception as e:
            errorMsg = f"Exception during AI request for <@{userId}>: {e}"
            logger.error(f"[mention] {errorMsg}")

            fallbackMsg = "You're lucky I'm too lazy to deal with you right now."
            say(fallbackMsg, thread_ts=threadTs)