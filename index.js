import dotenv from 'dotenv';
import pkg from '@slack/bolt';
import { register as mentionRegister} from './events/mention.js';
import { register as leetcodeRegister } from './events/leetcode.js';
import { register as joinedRegister } from './events/joined.js';
import { register as lastfmRegister } from './events/lastfm.js';
import { register as osuRegister } from './events/osu.js';
import { join } from 'path';

dotenv.config();

const { App } = pkg;

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  socketMode: true,
  appToken: process.env.SLACK_APP_TOKEN
});

mentionRegister(app);
leetcodeRegister(app);
joinedRegister(app);
lastfmRegister(app);
// osuRegister(app);

(async () => {
  await app.start();
  console.log('Bolt app is running');
})();