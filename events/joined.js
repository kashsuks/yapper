import dotenv from 'dotenv';
import { withBlacklistEvent } from './blacklist.js';
dotenv.config();

export function register(app) {
  app.event('member_joined_channel', withBlacklistEvent('member_joined', async ({ event, say, logger }) => {
    logger.info(event);
    const user = event.user;
    const channel = event.channel;

    try {
      const botUserId = (await app.client.auth.test()).user_id;

      const convoInfo = await app.client.conversations.info({ channel });
      const channelInfo = convoInfo.channel || {};
      const managerId = channelInfo.creator || event.inviter || botUserId; //if doesnt work then fallback to this

      await say({
      channel,
      text: `Hi <@${user}>, welcome to the land where <@${managerId}> does stupid shit`
      });
    } catch (err) {
      logger.error('Failed to post welcome message:', err);

      await say({
        channel,
        text: `Hi <@{user}>, welcome to the land where my creator does stupid shit`
      })
    }
  }));
}