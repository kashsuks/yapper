import requests
import re
from events.blacklist import isBlacklisted, blockIfBlacklisted

def register(app):
    @app.event("app_mention")
    @blockIfBlacklisted
    def mention(event, say, logger):
        userId = event["user"]
        fullText = event.get("text", "")
        threadTs = event.get("thread_ts") or event["ts"]
        botUserId = app.client.auth_test()["user_id"]
        strippedText = fullText.replace(f"<@{botUserId}>", "").strip()
        if strippedText == "":
            say(f"What the f**k is your problem <@{userId}>", thread_ts=threadTs)
        else:
            try:
                response = requests.post(
                    "https://ai.hackclub.com/chat/completions",
                    headers={"Content-type": "application/json"},
                    json={"messages": [{"role": "user", "content": f"Give me a bitchy and annoying karen like response. Only return the final response, not anything between <think> tags: {strippedText}"}]},
                    timeout=10
                )
                if response.ok:
                    aiReply = response.json()["choices"][0]["message"]["content"]
                    filteredReply = re.sub(r"<think>.*?</think>", "", aiReply, flags=re.DOTALL).strip()
                    if (filteredReply.startswith('"') and filteredReply.endswith('"')) or \
                       (filteredReply.startswith("'") and filteredReply.endswith("'")):
                        filteredReply = filteredReply[1:-1].strip()
                    say(filteredReply, thread_ts=threadTs)
                else:
                    logger.error("AI API returned error: " + response.text)
                    say("Shut up, even the AI doesn't want to respond to that.", thread_ts=threadTs)
            except Exception as e:
                logger.error("AI request failed: " + str(e))
                say("You're lucky I'm too lazy to deal with you right now.", thread_ts=threadTs)