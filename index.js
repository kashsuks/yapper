import 'dotenv/config';
import { App } from '@slack/bolt';
import { SocketModeHandler } from '@slack/bolt';
import logging from 'console';

//env variables

const {
    SLACK_BOT_TOKEN,
    SLACK_APP_TOKEN,
    LEETCODE_HANDLE,
    SLACK_USER_ID,
    SLACK_CHANNEL_IDS,
    LASTFM_USER,
    LASTFM_API_KEY,
    CLIENT_SECRET,
    CLIENT_ID,
    OSU_ID,
    OSU_V1_API,
    BLACKLISTED_CHANNEL_IDS,
    ROAST_CHANNEL_ID,
    ADMIN_PORT
} = process.env

//init bolt app

const app = new App({ token: SLACK_BOT_TOKEN });

// -- imports and event registration -- //
import * as mention from './events/mention.js'
import * as leetcode from './events/leetcode.js'
import * as joined from './events/joined.js'
import * as spotify from './events/spotify.js'
import * as leave from './events/leave.js'
import * as musicRoast from './events/musicRoast.js'
import * as leaderboard from './events/leaderboard.js'
import * as scoreSubmission from './events/scoreSubmission.js'

//register events
mention.register(app);
leetcode.register(app);
joined.register(app);
spotify.register(app);
osuSlack.register(app);
leave.register(app);
musicRoast.register(app);
leaderboard.register(app);
scoreSubmission.register(app);

(async () => {
  try {
    await app.start();
    logging.log('⚡️ Yapper Bot is running!');
  } catch (err) {
    logging.error('Unable to start Yapper Bot:', err);
  }
})();