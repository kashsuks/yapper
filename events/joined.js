import dotenv from 'dotenv';
dotenv.config();

export default {
  register(app) {
    app.event('member_joined_channel', async ({ event, say, logger }) => {
      logger.info(event);
      const user = event.user;
      const channel = event.channel;
      await say({
        channel,
        text: `Hi <@${user}>, welcome to the land where <@${process.env.SLACK_USER_ID}> writes shit code`
      });
    });
  }
};