import requests
import random
import time

BASE_RM_URL = "https://apps.runescape.com/runemetrics/profile/profile"

def fetch_total_xp(rsn, max_retries=5, delay=2):

    params = {
        "user": rsn,
        "activities": "0"
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(BASE_RM_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            total_xp = data.get('totalxp')

            return int(total_xp)
        
        except requests.RequestException as e:
            print(f"Error fetching XP for {rsn}")

            # Retry, exponential backoff
            sleep_time = delay + random.uniform(0, 1)
            print(f"{rsn}: retrying in {sleep_time:.1f}s")
            time.sleep(sleep_time)
            delay *= 2

    print(f"Failed to fetch XP for {rsn} after {max_retries} attempts. Profile likely private")
    return None