import 'dotenv/config';
import fetch from "node-fetch";
import { isChannelBlacklisted } from './blacklist.js';

const lastKnownRating = {};

function extractRating(data) {
  const userRank = data.userContestRanking;
  if (userRank && userRank.rating !== undefined) {
    return parseInt(userRank.rating, 10);
  }
  return null;
}

async function fetchLeetCodeRating(handle) {
  const url = `https://leetcode-api-pied.vercel.app/user/${handle}/contests`;
  try {
    const res = await fetch(url, { timeout: 10000 });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    return extractRating(data);
  } catch (err) {
    console.error(`Error fetching rating for ${handle}:`, err);
    return null;
  }
}

function startAutoRatingCheck(app) {
  console.log("Starting LeetCode rating checker...");

  const handle = process.env.LEETCODE_HANDLE;
  const slackUser = process.env.SLACK_USER_ID;
  const channelIds = process.env.SLACK_CHANNEL_IDS
    ? process.env.SLACK_CHANNEL_IDS.split(",").map((c) => c.trim())
    : [];

  if (!handle || !slackUser || channelIds.length === 0) {
    console.error(
      "Missing LEETCODE_HANDLE, SLACK_USER_ID, or SLACK_CHANNEL_IDS in environment variables"
    );
    return;
  }

  const CHECK_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours in ms

  async function check() {
    console.log("Checking rating...");
    const newRating = await fetchLeetCodeRating(handle);
    console.log("Current rating:", newRating);

    if (newRating !== null) {
      if (!(handle in lastKnownRating)) {
        lastKnownRating[handle] = newRating;
        console.log(`Initial rating set for ${handle}: ${newRating}`);
      } else {
        const prevRating = lastKnownRating[handle];
        const delta = newRating - prevRating;

        if (delta !== 0) {
          lastKnownRating[handle] = newRating;

          const emoji = delta >= 0 ? "📈" : "📉";
          const sign = delta >= 0 ? "+" : "";

          const message = `<@${slackUser}> ${emoji} LeetCode rating update: \`${prevRating}\` → \`${newRating}\` (${sign}${delta})`;

          for (const channelId of channelIds) {
            // Use the blacklist check function
            if (isChannelBlacklisted(channelId)) {
              console.log(
                `[BLACKLIST] Skipped LeetCode update in channel ${channelId}`
              );
              continue;
            }

            try {
              await app.client.chat.postMessage({
                channel: channelId,
                text: message,
              });
              console.log(`Sent rating update to channel ${channelId}`);
            } catch (err) {
              console.error(
                `Slack error posting to channel ${channelId}:`,
                err
              );
            }
          }
        } else {
          console.log("No rating change");
        }
      }
    } else {
      console.warn(`Could not fetch rating for ${handle}`);
    }

    setTimeout(check, CHECK_INTERVAL);
  }

  check();
}

export function register(app) {
  startAutoRatingCheck(app);
}