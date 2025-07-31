import dotenv from 'dotenv';
import fetch from 'node-fetch';
dotenv.config();

const lastfmUser = process.env.LASTFM_USER;
const lastfmApiKey = process.env.LASTFM_API_KEY;
const slackChannel = process.env.SLACK_CHANNEL_IDS;
const slackUser = process.env.SLACK_USER_ID;
const pollInterval = 15000;

let session = null;

async function getRecentTrack() {
  const url = `http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=${lastfmUser}&api_key=${lastfmApiKey}&format=json&limit=1`;
  const res = await fetch(url);
  const json = await res.json();
  return json.recenttracks?.track?.[0] || null;
}

function getUnixTimestamp() {
  return Math.floor(Date.now() / 1000);
}

function parseTimestamp(track) {
  if (track.date && track.date.uts) return parseInt(track.date.uts, 10);
  return getUnixTimestamp();
}

async function startSession(track, client) {
  const text = `<@${slackUser}> just started a new listening session (he is peak unemployed)`;
  const res = await client.chat.postMessage({ channel: slackChannel, text });
  return {
    startTime: getUnixTimestamp(),
    lastTime: getUnixTimestamp(),
    threadTs: res.ts,
    lastTrack: track.name || "",
  };
}

async function postTrack(track, threadTs, client) {
  const name = track.name || "Unknown";
  const artist = track.artist?.["#text"] || "Unknown";
  const url = track.url?.replace(/^"|"$/g, "") || "";
  const text = `*${artist}* – <${url}|${name}>`;
  await client.chat.postMessage({ channel: slackChannel, text, thread_ts: threadTs });
}

export function register(app) {
  const client = app.client;

  async function poll() {
    try {
      const track = await getRecentTrack();
      if (!track) return;

      const nowPlaying = track["@attr"]?.nowplaying === "true";
      const trackName = track.name;

      if (session) {
        if (getUnixTimestamp() - session.lastTime > 1800) {
          session = null;
        } else if (trackName !== session.lastTrack) {
          await postTrack(track, session.threadTs, client);
          session.lastTrack = trackName;
          session.lastTime = getUnixTimestamp();
        }
      } else if (nowPlaying) {
        session = await startSession(track, client);
        await postTrack(track, session.threadTs, client);
      }
    } catch (err) {
      console.error("Polling error:", err);
    }
  }

  setInterval(poll, pollInterval);
}