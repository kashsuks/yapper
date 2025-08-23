import axios from "axios";

const roastChannel = process.env.ROAST_CHANNEL_ID;
const lastfmApiKey = process.env.LASTFM_API_KEY;

async function getRecentTracks(user, limit = 10) {
  try {
    const resp = await axios.get("http://ws.audioscrobbler.com/2.0/", {
      params: {
        method: "user.getrecenttracks",
        user,
        api_key: lastfmApiKey,
        format: "json",
        limit
      },
      timeout: 10000
    });

    const data = resp.data;
    if (data.error) {
      console.error(`[musicRoast] Last.fm API error for ${user}: ${data.message}`);
      return [];
    }

    return data.recenttracks?.track || [];
  } catch (e) {
    console.error(`[musicRoast] Exception fetching tracks for ${user}: ${e}`);
    return [];
  }
}

function pickTrack(tracks) {
  if (!tracks.length) return null;
  const track = tracks[Math.floor(Math.random() * tracks.length)];
  const artist = track.artist?.["#text"] || "Unknown";
  const name = track.name || "Unknown";
  return `${artist} - ${name}`;
}

async function generateRoast(userId, track) {
  try {
    const resp = await axios.post(
      "https://ai.hackclub.com/chat/completions",
      {
        messages: [
          {
            role: "user",
            content: `Roast someone for listening to '${track}'. Be funny, sarcastic, and a bit mean but not too harsh. Keep it under 100 words. Don't use quotes around your response.`
          }
        ]
      },
      { timeout: 15000 }
    );

    if (resp.data?.choices?.[0]?.message?.content) {
      let roast = resp.data.choices[0].message.content.trim();
      roast = roast.replace(/<think>.*?<\/think>/gs, "").trim();
      if (
        (roast.startsWith('"') && roast.endsWith('"')) ||
        (roast.startsWith("'") && roast.endsWith("'"))
      ) {
        roast = roast.slice(1, -1).trim();
      }
      return `<@${userId}> ${roast}`;
    }

    return `yo <@${userId}> really spinning *${track}*? that's wild 💀`;
  } catch (e) {
    console.error(`[musicRoast] Exception generating roast for ${userId}: ${e}`);
    return `yo <@${userId}> really spinning *${track}*? that's questionable`;
  }
}

export function register(app) {
  app.event("message", async ({ event, client }) => {
    const channel = event.channel;
    const user = event.user;
    const text = (event.text || "").trim();
    const subtype = event.subtype;
    const thread_ts = event.thread_ts || event.ts;

    if (channel !== roastChannel || subtype === "bot_message" || !user) return;

    if (!text) {
      await client.chat.postMessage({
        channel,
        thread_ts,
        text: "Please provide your Last.fm username to get roasted!"
      });
      return;
    }

    const tracks = await getRecentTracks(text, 10);
    if (!tracks.length) {
      await client.chat.postMessage({
        channel,
        thread_ts,
        text: `Couldn't find what **${text}** has been listening to. Make sure that's your correct Last.fm username!`
      });
      return;
    }

    const track = pickTrack(tracks);
    if (!track) {
      await client.chat.postMessage({
        channel,
        thread_ts,
        text: "Something went wrong picking a track to roast"
      });
      return;
    }

    const roast = await generateRoast(user, track);
    await client.chat.postMessage({
      channel,
      thread_ts,
      text: roast
    });
  });
}