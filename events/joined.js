import dotenv from 'dotenv';
import { withBlacklistEvent } from './blacklist.js';
dotenv.config();

export function register(app) {
  app.event('member_joined_channel', withBlacklistEvent('member_joined', async ({ event, say, logger }) => {
    logger.info(event);
    const user = event.user;
    const channel = event.channel;
    await say({
      channel,
      text: `Hi <@${user}>, welcome to the land where <@${process.env.SLACK_USER_ID}> writes shit code`
    });
  }));
}