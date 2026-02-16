# Latest Python release
FROM python:3.15-rc-slim

# Prevent Python from buffering output
ENV PYTHONUNBUFFERED=1

# Working directory inside container
WORKDIR /app

# Install Linux dependencies
RUN apt-get update && apt-get install -y cron build-essential

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY scripts ./scripts

# Give cron script permissions
RUN chmod +x scripts/run_sync_cron.sh

# Default command: run the main sync script
CMD ["./scripts/run_sync_cron.sh"]