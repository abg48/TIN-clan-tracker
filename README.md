# TIN Bot

This project owns the Discord bot and event workflows for The Iron Nation.

Responsibilities:
- run slash commands and Discord UI flows
- handle clan events and automation
- query clan data through the sync API
- keep bot runtime separate from the data layer

This repo intentionally does not own the SQLite database or the nightly sync script.

## Local setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env
python -m app.bot
```

## Required environment variables

```bash
DISCORD_TOKEN=your_discord_token
SYNC_API_BASE_URL=http://localhost:8000
```

## Docker

```bash
docker build -t tin-bot .
docker run --rm -it --env-file .env tin-bot
```

## Notes

The bot expects the sync service to already be running and exposing a read-only API.

This keeps the bot deployable on AWS without moving the home-hosted database to the cloud.