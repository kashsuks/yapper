# Welcome to the Yapper Slack Bot Documentation

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [First Time Setup](#first-time-setup)
- [Commads](#commands)

## Requirements

The requirements for the Yapper bot are pretty simple.

- Latest Node.js version
- npm Package Manager
- Slack Account, Workspace, and the necessary permissions to create bots
- Git or Github Desktop

## Installation

In order to install the Yapper Slack bot, you must git clone it through the following command:

```bash
git clone https://github.com/kashsuks/yapper
```

Now we need to install all the dependencies in order to have the files for the API's and trackers working

```bash
npm install
```

In order to test and check whether or not your installation has issues, run:

```bash
node index.js
```

If the node setup works, then there should be no error messages displayed.

## Environment Variables

Since the bot depends on a lot of API's and secrets to do all the tracking features for music, osu! gameplay, etc, there are quite a few environment variables to consider.

Heres a snapshot of them.

```bash
SLACK_BOT_TOKEN=..
SLACK_APP_TOKEN=..
LEETCODE_HANDLE=.
SLACK_USER_ID=..
SLACK_CHANNEL_IDS=..
LASTFM_USER=..
LASTFM_API_KEY=..
CLIENT_SECRET=..
CLIENT_ID=..
OSU_ID=..
OSU_V1_API=..
BLACKLISTED_CHANNEL_IDS=..
ROAST_CHANNEL_ID=..
```

If you fill out these environment variables from the websites in the readme, your bot will work.

## Commands

Yapper is a Bot meaning it doesn't have its own commands, rather we assume that each action the bot carries out is a command.

### Join

When a user joins the channel that Yapper is currently in it sends a message pinging the user, below is the message:

```
Hi @<user>, welcome to the land where @<owner> writes shit code
```

You can change this message by going to `events/joined.py` and changing the string to your liking.

### Leave

If you want the bot to leave the channel, its quite simple, by using `/yapperLeave` (and making sure its setup in your Slack API), the bot will leave the channel the command was used in. Here is the message it displays:

```
Leaving #<channel name> now. Bye!
```

If you want to modify this message, head over to your `events/leave.py` file and changing the leave string as you want.