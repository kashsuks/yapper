import re

def register(app):
    @app.message(re.compile(r"\bbaking\b", re.IGNORECASE))
    def handle_baking_messages(message, say, event, logger, body):
        print(1)
        logger.info(body)
        channel = event["channel"]
        app.client.chat_postMessage(
            channel=channel,
            text=f"<#C094UD4EA1X>. Anyways, go join <#C08EZ3GJ5GV>"
        )