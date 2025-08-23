import axios from "axios";
import { withBlacklistCommand } from './blacklist.js';

function monthStartTs() {
  const now = new Date();
  const start = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1));
  return Math.floor(start.getTime() / 1000);
}

async function fetchMsgs(chanId, botToken) {
  const oldest = monthStartTs();
  let msgs = [];
  let cursor = undefined;

  while (true) {
    const params = { channel: chanId, oldest, limit: 200 };
    if (cursor) params.cursor = cursor;

    try {
      const res = await axios.get("https://slack.com/api/conversations.history", {
        headers: { Authorization: `Bearer ${botToken}` },
        params,
      });

      if (!res.data.ok) {
        console.error("[leaderboard] Error fetching messages:", res.data);
        break;
      }

      msgs = msgs.concat(res.data.messages || []);
      cursor = res.data.response_metadata?.next_cursor;
      if (!cursor) break;
    } catch (err) {
      console.error("[leaderboard] Exception fetching messages:", err);
      break;
    }
  }

  return msgs;
}

function buildLb(msgs) {
  const counts = {};
  for (const m of msgs) {
    const u = m.user;
    if (u) counts[u] = (counts[u] || 0) + 1;
  }
  return Object.entries(counts).sort((a, b) => b[1] - a[1]);
}

export function register(app) {
  app.command("/yapperleaderboard", withBlacklistCommand('yapperleaderboard', async ({ ack, body, respond }) => {
    ack();

    const chanId = body.channel_id;
    const botToken = process.env.SLACK_BOT_TOKEN;
    const msgs = await fetchMsgs(chanId, botToken);
    const lb = buildLb(msgs).slice(0, 10);

    if (!lb.length) {
      await respond(":speech_balloon: no msgs this month");
      return;
    }

    let text = ":speech_balloon: *Yapper Leaderboard (Top 10 this month)*\n";
    lb.forEach(([user, count], i) => {
      text += `${i + 1}. <@${user}> — ${count} msgs\n`;
    });

    await respond(text);
  }));
}