import 'dotenv/config';

let blacklistedChannels = process.env.BLACKLISTED_CHANNEL_IDS
  ? process.env.BLACKLISTED_CHANNEL_IDS.split(",").map(c => c.trim())
  : [];

export function withBlacklist(actionName, fn) {
  return async (app, context) => {
    const channelId = context?.channel || context?.body?.event?.channel;

    if (blacklistedChannels.includes(channelId)) {
      console.log(`[BLACKLIST] Skipped ${actionName} in channel ${channelId}`);
      return;
    }

    return fn(app, context);
  };
}

// Hot reload blacklist dynamically
export function reloadBlacklist() {
  blacklistedChannels = process.env.BLACKLISTED_CHANNEL_IDS
    ? process.env.BLACKLISTED_CHANNEL_IDS.split(",").map(c => c.trim())
    : [];
  console.log("Reloaded blacklist:", blacklistedChannels);
}