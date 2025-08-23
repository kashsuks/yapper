import fetch from 'node-fetch';
import fs from 'fs';

const BLACKLIST_FILE = './blacklist.json';

// Load blacklist dynamically
function loadBlacklist() {
  try {
    if (fs.existsSync(BLACKLIST_FILE)) {
      return JSON.parse(fs.readFileSync(BLACKLIST_FILE, 'utf8'));
    }
  } catch (err) {
    console.error('Error loading blacklist:', err);
  }
  return { channels: [], actions: [] };
}

export function register(app) {
  app.event('app_mention', async ({ event, say, logger }) => {
    const blacklist = loadBlacklist();

    // Skip if the action or channel is blacklisted
    if (
      blacklist.actions?.includes('mention') &&
      blacklist.channels?.includes(event.channel)
    ) {
      console.log(`Skipping mention in blacklisted channel ${event.channel}`);
      return;
    }

    const userId = event.user;
    const fullText = event.text || '';
    const threadTs = event.thread_ts || event.ts;

    const botUserId = (await app.client.auth.test()).user_id;
    const strippedText = fullText.replace(`<@${botUserId}>`, '').trim();

    if (!strippedText) {
      await say({ text: `What the f**k is your problem <@${userId}>`, thread_ts: threadTs });
      return;
    }

    try {
      const response = await fetch('https://ai.hackclub.com/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [
            {
              role: 'user',
              content: `Give me a passive aggressive karen annoying like response for the following text. Only return the final response, not anything between <think> tags: ${strippedText}`
            }
          ]
        }),
        timeout: 10000
      });

      if (!response.ok) throw new Error(await response.text());

      const aiReply = (await response.json()).choices[0].message.content;
      const filtered = aiReply.replace(/<think>.*?<\/think>/gs, '').trim().replace(/^['"]|['"]$/g, '');
      await say({ text: filtered, thread_ts: threadTs });
    } catch (err) {
      logger.error(err);
      await say({ text: "You're lucky I'm too lazy to deal with you right now.", thread_ts: threadTs });
    }
  });
}