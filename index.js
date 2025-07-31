import dotenv from 'dotenv';
import pkg from '@slack/bolt';
import mention from './events/mention.js';
import { register as leetcodeRegister } from './events/leetcode.js';
import joined from './events/joined.js';
import { register as lastfmRegister } from './events/lastfm.js';

dotenv.config();

const { App } = pkg;

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  socketMode: true,
  appToken: process.env.SLACK_APP_TOKEN
});

mention.register(app);
leetcodeRegister(app);
joined.register(app);
lastfmRegister(app);

(async () => {
  await app.start();
  console.log('Bolt app is running');
})();