# use this to swear at the dumbass who pinged you

def register(app):
    @app.event("app_mention")
    def mention(event, say):
        user = event["user"]
        threadTs = event.get("thread_ts") or event["ts"]
        say(f"What the f**k is your problem <@{user}>", thread_ts = threadTs)