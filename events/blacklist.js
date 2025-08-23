import 'dotenv/config';

let blacklistedChannels = process.env.BLACKLISTED_CHANNEL_IDS
  ? process.env.BLACKLISTED_CHANNEL_IDS.split(",").map(c => c.trim())
  : [];

// Generic blacklist wrapper that works with different Slack event types
export function withBlacklist(actionName, fn) {
  return async (app, context) => {
    // Extract channel ID from various possible locations
    const channelId = 
      context?.channel ||           // Direct channel property
      context?.body?.channel_id ||  // Slash commands
      context?.event?.channel ||    // Events like mentions, messages
      context?.body?.event?.channel; // Nested events

    if (blacklistedChannels.includes(channelId)) {
      console.log(`[BLACKLIST] Skipped ${actionName} in channel ${channelId}`);
      return;
    }

    return fn(app, context);
  };
}

// Specialized wrapper for Slack Bolt event handlers
export function withBlacklistEvent(actionName, handler) {
  return async (eventData) => {
    const { event } = eventData;
    const channelId = event?.channel;

    if (blacklistedChannels.includes(channelId)) {
      console.log(`[BLACKLIST] Skipped ${actionName} in channel ${channelId}`);
      return;
    }

    return handler(eventData);
  };
}

// Specialized wrapper for Slack Bolt command handlers
export function withBlacklistCommand(actionName, handler) {
  return async (commandData) => {
    const { body } = commandData;
    const channelId = body?.channel_id;

    if (blacklistedChannels.includes(channelId)) {
      console.log(`[BLACKLIST] Skipped ${actionName} in channel ${channelId}`);
      return;
    }

    return handler(commandData);
  };
}

// Simple check function for channels
export function isChannelBlacklisted(channelId) {
  return blacklistedChannels.includes(channelId);
}

// Hot reload blacklist dynamically
export function reloadBlacklist() {
  blacklistedChannels = process.env.BLACKLISTED_CHANNEL_IDS
    ? process.env.BLACKLISTED_CHANNEL_IDS.split(",").map(c => c.trim())
    : [];
  console.log("Reloaded blacklist:", blacklistedChannels);
}