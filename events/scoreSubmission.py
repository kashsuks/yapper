import os
from slack_bolt import App
from slack_sdk.errors import SlackApiError

rhythmChannel = os.getenv("RHYTHM_CHANNEL")  # channel where submissions go

def register(app: App):

    @app.command("/submit-score")
    def openScoreModal(ack, body, client):
        ack()
        try:
            client.views_open(
                trigger_id=body["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": "submit_score_modal",
                    "title": {"type": "plain_text", "text": "Submit Rhythm Score"},
                    "submit": {"type": "plain_text", "text": "Submit"},
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "blocks": [
                        {
                            "type": "input",
                            "block_id": "game_block",
                            "element": {
                                "type": "static_select",
                                "action_id": "game",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select a game"
                                },
                                "options": [
                                    {"text": {"type": "plain_text", "text": "osu!"}, "value": "osu!"},
                                    {"text": {"type": "plain_text", "text": "Beat Saber"}, "value": "Beat Saber"},
                                    {"text": {"type": "plain_text", "text": "Geometry Dash"}, "value": "Geometry Dash"},
                                    {"text": {"type": "plain_text", "text": "Other"}, "value": "Other"}
                                ]
                            },
                            "label": {"type": "plain_text", "text": "What rhythm game is this?"}
                        },
                        {
                            "type": "input",
                            "block_id": "pp_block",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "pp",
                                "placeholder": {"type": "plain_text", "text": "Enter performance points (integer)"}
                            },
                            "label": {"type": "plain_text", "text": "Performance Points / Equivalent"}
                        },
                        {
                            "type": "input",
                            "block_id": "link_block",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "link",
                                "placeholder": {"type": "plain_text", "text": "Link to the score"}
                            },
                            "label": {"type": "plain_text", "text": "Score Link"}
                        },
                        {
                            "type": "input",
                            "block_id": "like_block",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "like",
                                "multiline": True,
                                "placeholder": {"type": "plain_text", "text": "What did you like about this score?"}
                            },
                            "label": {"type": "plain_text", "text": "What did you like about this score?"}
                        }
                    ]
                }
            )
        except SlackApiError as e:
            print(f"Error opening modal: {e.response['error']}")

    @app.view("submit_score_modal")
    def handleScoreSubmission(ack, body, client, view):
        errors = {}
        stateValues = view["state"]["values"]

        ppStr = stateValues["pp_block"]["pp"]["value"]
        try:
            ppInt = int(ppStr)
            if ppInt < 0:
                errors["pp_block"] = "Performance points must be a positive integer."
        except ValueError:
            errors["pp_block"] = "Performance points must be an integer."

        link = stateValues["link_block"]["link"]["value"]
        if not link.startswith("http://") and not link.startswith("https://"):
            errors["link_block"] = "Please provide a valid link."

        if errors:
            ack(response_action="errors", errors=errors)
            return
        else:
            ack()

        user = body["user"]["id"]
        game = stateValues["game_block"]["game"]["selected_option"]["value"]
        liked = stateValues["like_block"]["like"]["value"]

        text = (
            f"New Score! <@{user}> just made a new {ppInt} play for the game {game}!!\n"
            f"They liked this because: {liked}\n\n"
            f"<{link}|Here> is their score! Show some love and appreciation!"
        )

        try:
            client.chat_postMessage(
                channel=rhythmChannel,
                text=text
            )
        except SlackApiError as e:
            print(f"Error posting score: {e.response['error']}")