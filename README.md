# TIN-clan-tracker (Better Name Pending)

Welcome to The Iron Nation's clan tracker, a tool put together to address the (hopefully temporary) lack of inactivity tracking functionality in Elenora's absence & Runepixel's API struggles.

The tool in it's current state is built as an "out-of-the box" capability. In the case of abg's untimely demise, following the instructions below should replicate things for the clan going forward

## Table of Contents

1. Prerequisites
2. Clone the Repository
3. Prepare the Database
4. Build and Run the Docker Container
5. Verify Functionality
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

## Prepare the Database

1. Create a data/ folder in the project root:
```bash
mkdir data
```
2. Copy the database to the new data folder
3. Optionally, should the database have been lost, a script is provided to provision a new blank db:
```bash
python3 ./app/db/db_init.py
```

## Build and Run the Docker Container
```bash
sudo docker compose build
sudo docker compose up -d
```
- The container runs in detached mode (-d)
- Cron inside the container is automatically configured to handle nightly API scrapes, no further action is required at this point beyond testing
- The data/ folder is mounted, so SQLite db & chron logs are persistent

## Verify Functionality
Check the containers status:
```bash
sudo docker compose ps
```
Check logs for any errors:
```bash
sudo docker compose logs -f
```

## Manual Sync
To test or run an API sync immediately:
```bash
sudo docker compose exec clan_sync python3 /app/app/sync/sync.py
```
This runs a manual full-clan scrape & updates the db without waiting for the normal nightly run. NOTE: Currently this takes anywhere from 30 minutes to an hour

## Troubleshooting
Why are you here my code is without flaw >.>