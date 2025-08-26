# Yapper Slack Bot Documentation

## Table of Contents
- [Requirements](#requirements)
- [Environment Variables](#environment-variables)
- [First Time Setup](#first-time-setup)
- [File Overview](#file-overview)
- [Commands & Behaviors](#commands-behaviors)
- [Troubleshooting](#troubleshooting)

---

## Requirements

The requirements for the Yapper bot are pretty simple:

- Latest [node.js](https://nodejs.org/en/download) version
- [npm](https://www.npmjs.com/) package manager
- Slack Account, Workspace, and permissions to create bots
- Git or GitHub Desktop

---

---

## Environment Variables

Since the bot depends on multiple APIs, there are quite a few environment variables to configure.  
Create a `.env` file in your project root:

```dotenv
# Slack
SLACK_BOT_TOKEN=xoxb...
SLACK_APP_TOKEN=xapp...
SLACK_USER_ID=...
SLACK_CHANNEL_IDS=...,...

# Last.fm
LASTFM_USER=...
LASTFM_API_KEY=...

# LeetCode
LEETCODE_HANDLE=...

# Last.fm Roasting
ROAST_CHANNEL_ID=...

# Signing
SIGNING_SECRET=...

# Blacklisting and other safety features
BLACKLISTED_CHANNEL_IDS=...

```

Here is where you can get the API keys for all the API's used in the bot:

- [Slack API](https://api.slack.com/apps)
- [Last.fm](https://www.last.fm/api/account/create)

---

## First Time Setup

- **Create a Slack App**
	- Go to your Slack developer portal and create a new app (from scratch).
  	- Enable **Socket Mode** and generate an **App-Level Token** with the scope `connections:write`.

2. **Bot Token Scopes**
	Add the following **Bot Token Scopes** under *OAuth & Permissions*:
	- `chat:write`
	- `app_mentions:read`
	- `channels:read`, `groups:read`, `im:read`, `mpim:read`
	- `channels:history`, `groups:history`, `im:history`, `mpim:history`
	- `channels:join`
	- `commands`

3. **Event Subscriptions**
	- Subscribe to:
		- `member_joined_channel`
		- `app_mention`

4. **Slash Commands**
	- Create `/yapperLeave` in the Slack App settings.
	- Create `/yapperleaderboard` in the Slack App settings.
	- Create `/submit-score` in the Slack App settings.

5. **Install the Dependencies**


5. **Run the Bot**
	- ```
	node index.js
	```

---

## File Overview

- **`index.js`** – Entrypoint for the bot, deals with all the event handling and bot registration
- **`events/`**
	- `joined.js` – Handles welcome messages.
	- `leave.js` – Handles leave command.
	- `blacklist.js` – Defines blacklisted channel logic.
	- `leaderboard.js` - Used for finding the leaderboard of messages in the last month.
	- `blacklist.js` - Blacklists certain actions in channels
	- `mention.js` - AI responses by [Hack Club AI](https://ai.hackclub.com)
	- `musicRoast.js` - Music roasts in specific channels (support by Last.fm API)
	- `scoreSubmission.js` - From like slash-command for rhythm game score submissions
	- `leetcode.js` - Updated LeetCode rating every 24 hours
	- `quote.js` - Timely quotes by the bot and also by a slash comamnd
- **`docs/`** – Documentation sources for GitHub Pages (MkDocs/Jekyll).

---

## Commands & Behaviors

### Join (Welcome)
When a user joins a channel:

```
Hi <@user>, welcome to the land where <@owner> writes shit code
```

This action is compatible with the blacklist feature, meaning that if a channel is in the blacklist channel ids and a user joins the channel, the join message will **NOT** be triggered.

**Change in `events/joined.js`.**

*Future plans are to change the <@owner> ping to channel manager*

---

### Leave (Slash Command)
Use `/yapperLeave` to make Yapper leave from the channel the user is currently in:

```
Leaving #<channel name> now. Bye!
```

This action is compatible with the blacklist feature, meaning that if a channel is in the balcklist channel ids and a user joins the channel, the join message will **NOT** be triggered.

**Change in `events/leave.js`.**

---

### Last.fm — Now Playing Tracker
- Polls your Last.fm recent track.
- Posts updates every 15s when the track changes.
- Posts only in `SLACK_CHANNEL_IDS`

*Tip:* To post **privately only to you**, replace `chat.postMessage` with `chat.postEphemeral` in the code.

**Only happens when the user (me) is listening to music**

This action is compatible with the blacklist feature, meaning that if a channel is in the blacklist channel ids and a user joins the channel, the join message will **NOT** be triggered.

**Change in `events/lastfm.js`**

---

---

### Roast
- Posts roast messages in the channel defined by `ROAST_CHANNEL_ID`. Currently it is [a dedicated roast channel](https://hackclub.slack.com/archives/C09AM3PDZ0B) in which you can post your Last.fm username for it to roast you.

---

### Channel Blacklist
- Yapper never posts in channels listed in `BLACKLISTED_CHANNEL_IDS`.

---

---

---

### Leaderboard

You can check the messages leaderboard for the past month by running `/yapperleaderboard`. The message is by default only displayed to the user that runs it. The Slack API rate limits it to 1 request every 10 seconds so keep that in mind.

*Change in* `events/leaderboard.py`.

---

### Pinging and AI Responses

By pinging `@Yapper` by itself, the bot responds with `What the f**k is your problem @<user>`, but if you put any text beside the ping. For example `@Yapper hi`, the bot will generate and display a response using [the Hack Club AI](https://ai.hackclub.com)

## Troubleshooting

- **Bot doesn’t post**
  - Check `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`.
  - Ensure bot is invited to the channel.
  - Make sure channel is not blacklisted.

- **Private posts only**
  - Use `chat.postEphemeral` instead of `chat.postMessage`.

- **Welcome/Leave not firing**
  - Verify event subscriptions + `/yapperLeave` slash command is set up.