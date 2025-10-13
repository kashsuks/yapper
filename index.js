import dotenv from "dotenv";
import pkg from "@slack/bolt";
import { register as mentionRegister } from "./events/mention.js";
import { register as leetcodeRegister } from "./events/leetcode.js";
import { register as joinedRegister } from "./events/joined.js";
import { register as spotifyRegister } from "./events/lastfm.js";
import { register as leaveRegister } from "./events/leave.js";
import { register as musicRoastRegister } from "./events/musicRoast.js";
import { register as leaderboardRegister } from "./events/leaderboard.js";
import { register as scoreSubmissionRegister } from "./events/scoreSubmission.js";
import { register as quoteRegister } from "./events/quote.js";
import { register as javaRegister } from "./events/java.js";

dotenv.config();

const { App } = pkg;

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  socketMode: true,
  appToken: process.env.SLACK_APP_TOKEN,
});

// initialize all the different subcommands/subactions
mentionRegister(app);
leetcodeRegister(app);
joinedRegister(app);
spotifyRegister(app);
leaveRegister(app);
musicRoastRegister(app);
leaderboardRegister(app);
scoreSubmissionRegister(app);
quoteRegister(app);
javaRegister(app);

(async () => {
  await app.start();
  console.log("Bolt app is running");
})();
