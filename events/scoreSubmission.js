import pkg from "@slack/bolt";
const { App } = pkg;

const rhythmChannel = process.env.RHYTHM_CHANNEL;

export function register(app) {
  app.command("/submit-score", async ({ ack, body, client }) => {
    await ack();
    try {
      await client.views.open({
        trigger_id: body.trigger_id,
        view: {
          type: "modal",
          callback_id: "submit_score_modal",
          title: { type: "plain_text", text: "Submit Rhythm Score" },
          submit: { type: "plain_text", text: "Submit" },
          close: { type: "plain_text", text: "Cancel" },
          blocks: [
            {
              type: "input",
              block_id: "game_block",
              element: {
                type: "static_select",
                action_id: "game",
                placeholder: { type: "plain_text", text: "Select a game" },
                options: [
                  { text: { type: "plain_text", text: "osu!" }, value: "osu!" },
                  { text: { type: "plain_text", text: "Beat Saber" }, value: "Beat Saber" },
                  { text: { type: "plain_text", text: "Geometry Dash" }, value: "Geometry Dash" },
                  { text: { type: "plain_text", text: "Other" }, value: "Other" }
                ]
              },
              label: { type: "plain_text", text: "What rhythm game is this?" }
            },
            {
              type: "input",
              block_id: "pp_block",
              element: {
                type: "plain_text_input",
                action_id: "pp",
                placeholder: { type: "plain_text", text: "Enter performance points (integer)" }
              },
              label: { type: "plain_text", text: "Performance Points / Equivalent" }
            },
            {
              type: "input",
              block_id: "link_block",
              element: {
                type: "plain_text_input",
                action_id: "link",
                placeholder: { type: "plain_text", text: "Link to the score" }
              },
              label: { type: "plain_text", text: "Score Link" }
            },
            {
              type: "input",
              block_id: "like_block",
              element: {
                type: "plain_text_input",
                action_id: "like",
                multiline: true,
                placeholder: { type: "plain_text", text: "What did you like about this score?" }
              },
              label: { type: "plain_text", text: "What did you like about this score?" }
            }
          ]
        }
      });
    } catch (e) {
      console.error("Error opening modal:", e?.data?.error || e);
    }
  });

  app.view("submit_score_modal", async ({ ack, body, view, client }) => {
    const stateValues = view.state.values;
    const errors = {};

    const ppStr = stateValues.pp_block.pp.value;
    let ppInt;
    try {
      ppInt = parseInt(ppStr, 10);
      if (ppInt < 0) errors.pp_block = "Performance points must be a positive integer.";
    } catch {
      errors.pp_block = "Performance points must be an integer.";
    }

    const link = stateValues.link_block.link.value;
    if (!link.startsWith("http://") && !link.startsWith("https://")) {
      errors.link_block = "Please provide a valid link.";
    }

    if (Object.keys(errors).length > 0) {
      await ack({ response_action: "errors", errors });
      return;
    } else {
      await ack();
    }

    const user = body.user.id;
    const game = stateValues.game_block.game.selected_option.value;
    const liked = stateValues.like_block.like.value;

    const text = `New Score! <@${user}> just made a new ${ppInt} play for the game ${game}!!
They liked this because: ${liked}

<${link}|Here> is their score! Show some love and appreciation!`;

    try {
      await client.chat.postMessage({
        channel: rhythmChannel,
        text
      });
    } catch (e) {
      console.error("Error posting score:", e?.data?.error || e);
    }
  });
}