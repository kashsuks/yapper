import fs from "fs";
import dotenv from "dotenv";

let blacklistCache = new Set();
let lastLoaded = 0;
const envPath = process.env.ENV_PATH || ".env";

export function loadBlacklist() {
    dotenv.config({ path: envPath, override: true });
    const channels = process.env.BLACKLISTED_CHANNEL_IDS || "";
    blacklistCache = new Set(
        channels.split(",").map((ch) => ch.trim()).filter((ch) => ch)
    );
    try {
        lastLoaded = fs.statSync(envPath).mtimeMs;
    } catch (err) {
        lastLoaded = Date.now();
    }
}

loadBlacklist();

export function isBlacklisted(channelId) {
    try {
        const mtime = fs.statSync(envPath).mtimeMs;
        if (mtime !== lastLoaded) {
            loadBlacklist();
        }
    } catch {}
    return blacklistCache.has(channelId);
}

export function blockIfBlacklisted(handler) {
  return function (...args) {
    const event = args[0] || {};
    const channelId = event.channel || null;
    if (channelId && isBlacklisted(channelId)) {
      return;
    }
    return handler(...args);
  };
}