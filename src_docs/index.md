---
layout: default
title: Yapper Slack Bot
nav_order: 1
---

# Yapper Slack Bot Documentation

Refer to [the website](https://kashsuks.github.io/yapper) for better documentation

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [First Time Setup](#first-time-setup)
- [File Overview](#file-overview)
- [Commands & Behaviors](#commands-behaviors)
- [Configuration Examples](#configuration-examples)
- [Running & Deployment](#running-deployment)
- [Troubleshooting](#troubleshooting)

---

## Requirements

The requirements for the Yapper bot are pretty simple:

- Latest **Python 3** version
- `pip` Package Manager
- Slack Account, Workspace, and permissions to create bots
- Git or GitHub Desktop

---

## Installation

Clone the repository:

```bash
git clone https://github.com/kashsuks/yapper
cd yapper
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Yapper locally:

```bash
python main.py
```

If the setup works, there should be no error messages displayed.

---

## Environment Variables

Since the bot depends on multiple APIs, there are quite a few environment variables to configure.  
Create a `.env` file in your project root:

```dotenv
# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-level-token
SLACK_USER_ID=U0123ABCD
SLACK_CHANNEL_IDS=C0123ABCD,C0456EFGH
BLACKLISTED_CHANNEL_IDS=C0NOPOST1,C0NOPOST2

# Last.fm
LASTFM_USER=your_lastfm_username
LASTFM_API_KEY=your_lastfm_api_key

# LeetCode
LEETCODE_HANDLE=your_leetcode_username

# osu!
OSU_ID=123456
OSU_V1_API=your_osu_v1_api_key
CLIENT_ID=your_osu_oauth_client_id
CLIENT_SECRET=your_osu_oauth_client_secret

# Fun
ROAST_CHANNEL_ID=C0ROASTME
```

---

## First Time Setup

1. **Create a Slack App**
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

5. **Run the Bot**
   ```bash
   python main.py
   ```

---

## File Overview

- **`main.py`** – Entrypoint, configures Slack Bolt App and SocketModeHandler.
- **`events/`**
  - `joined.py` – Handles welcome messages.
  - `leave.py` – Handles leave command.
  - `blacklist.py` – Defines blacklisted channel logic.
  - other integrations: Last.fm, osu!, LeetCode.
- **`admin/`**
  - `logs.py` – Logging utilities (`addLog`).
- **`requirements.txt`** – Python dependencies.
- **`docs/`** – Documentation sources for GitHub Pages (MkDocs/Jekyll).

---

## Commands & Behaviors

### Join (Welcome)
When a user joins a channel:
```
Hi @<user>, welcome to the land where @<owner> writes shit code
```
*Change in* `events/joined.py`.

---

### Leave (Slash Command)
Use `/yapperLeave` to make Yapper leave:
```
Leaving #<channel name> now. Bye!
```
*Change in* `events/leave.py`.

---

### Last.fm — Now Playing Tracker
- Polls your Last.fm recent track.
- Posts updates every 15s when the track changes.
- Posts only in `SLACK_CHANNEL_IDS`, skips `BLACKLISTED_CHANNEL_IDS`.

*Tip:* To post **privately only to you**, replace `chat.postMessage` with `chat.postEphemeral` in the code.

**Only happens when the user (me) is listening to music**

---

### osu! — Stats/Plays
- Uses `OSU_ID` + `OSU_V1_API` or `CLIENT_ID`/`CLIENT_SECRET`.
- Posts plays and PP changes in allowed channels.

**Only happens when the user, me is playing osu**

---

---

### Roast
- Posts roast messages in the channel defined by `ROAST_CHANNEL_ID`. Currently it is [a dedicated roast channel](https://hackclub.slack.com/archives/C09AM3PDZ0B) in which you can post your Last.fm username for it to roast you.

---

### Channel Blacklist
- Yapper never posts in channels listed in `BLACKLISTED_CHANNEL_IDS`.

---

---

### Leaderboard

You can check the messages leaderboard for the past month by running `/yapperleaderboard`

*Change in* `events/leaderboard.py`.

---

### Pinging and AI Responses

By pinging `@Yapper` by itself, the bot responds with `What the f**k is your problem @<user>`, but if you put any text beside the ping. For example `@Yapper hi`, the bot will generate and display a response using [the Hack Club AI](ai.hackclub.com)

## Configuration Examples

### `.env` Example
```dotenv
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
SLACK_USER_ID=U1234567
SLACK_CHANNEL_IDS=C0123ABCD,C0456EFGH
BLACKLISTED_CHANNEL_IDS=C0NOPOST1,C0NOPOST2
LASTFM_USER=myuser
LASTFM_API_KEY=myapikey
LEETCODE_HANDLE=myhandle
OSU_ID=123456
OSU_V1_API=osuapikey
CLIENT_ID=osuoauthid
CLIENT_SECRET=osuoauthsecret
ROAST_CHANNEL_ID=C0ROAST
```

---

## Running & Deployment

### Local
```bash
pip install -r requirements.txt
python main.py
```

### Systemd (Server)
`~/.config/systemd/user/yapper.service`:
```ini
[Unit]
Description=Yapper Slack Bot
After=network.target

[Service]
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=%h/yapper
ExecStart=/usr/bin/python3 %h/yapper/main.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
```

Enable + start:
```bash
systemctl --user daemon-reload
systemctl --user enable --now yapper
```

---

## Troubleshooting

- **Bot doesn’t post**
  - Check `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`.
  - Ensure bot is invited to the channel.
  - Make sure channel is not blacklisted.

- **Private posts only**
  - Use `chat.postEphemeral` instead of `chat.postMessage`.

- **Welcome/Leave not firing**
  - Verify event subscriptions + `/yapperLeave` slash command is set up.