# TIN-clan-tracker (Better Name Pending)

Welcome to The Iron Nation's clan tracker, a tool put together to address the (hopefully temporary) lack of inactivity tracking functionality in Elenora's absence & Runepixel's API struggles.

The project has been structured around a clear split between the sync layer and the Discord bot layer:

- `sync` owns the nightly RuneMetrics roster and XP sync, writes to SQLite, and exposes read-only data through an API
- `bot` consumes that API and handles Discord commands, admin flows, and clan event workflows
- the database remains local to the sync machine, which keeps AWS costs low while preserving bot resiliency in the cloud

## Table of Contents

1. Prerequisites
2. Clone the Repository
3. Local Sync + API Setup
4. Bot Setup
5. AWS Deployment Notes
6. Manual Sync
7. Troubleshooting

---

## Prerequisites

Make sure you have the following installed on whatever hardware will be running the tool:

- [Docker](https://www.docker.com/) (latest stable version)
- [Docker Compose](https://docs.docker.com/compose/)
- Git
- Optionally, Python for testing scripts outside docker

---

## Clone the Repository

On your host machine:

```bash
git clone https://github.com/abg48/TIN-clan-tracker.git
cd TIN-clan-tracker
```

## Local Sync + API Setup

The sync service remains responsible for updating the local SQLite database. A lightweight API is also exposed so the bot can query data without directly touching the database.

```bash
sudo docker compose up -d --build
```

This starts:

- `sync`: nightly local runner for roster + XP syncs
- `api`: read-only data API (`http://localhost:8000`)
- `bot`: Discord bot consumer that reads from `SYNC_API_BASE_URL`

The API exposes endpoints such as:

- `GET /health`
- `GET /members`
- `GET /member/{rsn}`
- `GET /leaderboard`
- `GET /inactive-members`
- `GET /xp-history/{rsn}`

The bot reads from the API by setting `SYNC_API_BASE_URL` in the environment, such as:

```bash
export SYNC_API_BASE_URL=http://localhost:8000
```

When the bot is moved to AWS, set the same variable to the public HTTPS URL of the local API or an API gateway in front of it.

## Bot Setup

The bot itself does not own the database and should operate in read-only mode against the sync API. For local development, the default compose config already does this:

```yaml
SYNC_API_BASE_URL=${SYNC_API_BASE_URL:-http://api:8000}
```

If you run the bot outside Docker, set the env var before starting it with Python.

## AWS Deployment Notes

The recommended deployment model is:

- keep the SQLite database and sync job on local infrastructure
- run the Discord bot on AWS using the same codebase/repo but with `SYNC_API_BASE_URL` pointed to the remote API
- keep the bot stateless and cache-only as needed during event bursts
- store secrets like `DISCORD_TOKEN` in AWS Secrets Manager or environment injection, not in the database

This avoids AWS database charges while keeping the bot highly available when clan events spike.

## Manual Sync

To test or run an API sync immediately:

```bash
sudo docker compose exec sync python3 -m app.main
```

This runs a manual full-clan scrape & updates the db without waiting for the normal nightly run. NOTE: Currently this takes anywhere from 30 minutes to an hour.

## Troubleshooting

If the bot cannot reach the sync API, verify:

```bash
curl http://localhost:8000/health
```

If that fails, confirm the API service is running and that `SYNC_API_BASE_URL` is configured correctly.

If the sync job is not updating data, check the sync container logs:

```bash
sudo docker compose logs -f sync
```

And for the API:

```bash
sudo docker compose logs -f api
```

Why are you here my code is without flaw >.>