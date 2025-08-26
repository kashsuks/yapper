import fetch from "node-fetch";
import cron from "node-cron";
import { withBlacklistEvent } from "./blacklist.js";

async function getQuote() {
  const res = await fetch("http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en");
  let raw = await res.text();
  raw = raw.replace(/\\'/g, "'").replace(/\\"/g, '"');
  const data = JSON.parse(raw);

  const text = data.quoteText.trim();
  const author = data.quoteAuthor ? `— *${data.quoteAuthor}*` : "— Unknown";
  return `${text}\n${author}`;
}

export function register(app) {
  app.command(
    "/yapperquote",
    withBlacklistEvent("quote_command", async ({ ack, respond, logger }) => {
      await ack();

      try {
        const quote = await getQuote();
        await respond({ text: quote });
      } catch (err) {
        logger.error(err);
        await respond("Failed to fetch a quote. Try again later.");
      }
    })
  );

  app.message(
    /quote please/i,
    withBlacklistEvent("quote_request", async ({ message, say, logger }) => {
      try {
        const quote = await getQuote();
        await say({ channel: message.channel, text: quote });
      } catch (err) {
        logger.error(err);
        await say("Couldn’t fetch a quote right now.");
      }
    })
  );

  cron.schedule("0 9 * * *", async () => {
    try {
      const quote = await getQuote();
      await app.client.chat.postMessage({
        channel: process.env.QUOTE_CHANNEL_ID,
        text: quote
      });
    } catch (err) {
      console.error("Failed to send scheduled quote", err);
    }
  }, {
    timezone: "America/New_York"
  });
}