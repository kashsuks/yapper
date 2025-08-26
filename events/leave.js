import { withBlacklistCommand } from './blacklist.js';

export function register(app) {
  app.command("/yapperleave", withBlacklistCommand('yapperleave', async ({ ack, body, client, respond }) => {
    await ack();
    const channelId = body.channel_id;

    try {
      await client.chat.postMessage({
        channel: channelId,
        text: `👋 Leaving <#${channelId}> now. Bye!`
      });

      await client.conversations.leave({ channel: channelId });

      console.log(`[leave] Bot left channel ${channelId}`);
    } catch (e) {
      console.error(`[leave] Failed to leave channel ${channelId}: ${e}`);
      await respond(`⚠️ Error: ${e}`);
    }
  }));
}