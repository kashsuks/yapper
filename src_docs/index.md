# Welcome to the Yapper Slack Bot Documentation

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [First Time Setup](#first-time-setup)

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

It's better to run the install command in a virtual environment, but it is not necessary.

## Environment Variables

Since the bot depends on a lot of API's and secrets to do all the tracking features for music, osu! gameplay, etc, there are quite a few environment variables to consider.

Heres a snapshot of them.

```bash
SLACK_BOT_TOKEN=..
SLACK_APP_TOKEN=..
LEETCODE_HANDLE=..
SLACK_USER_ID=..
SLACK_CHANNEL_IDS=..
LASTFM_USER=..
LASTFM_API_KEY=..
CLIENT_SECRET=..
CLIENT_ID=..
OSU_ID=..
```

If you fill out these environment variables from the websites in the readme, your bot will work.