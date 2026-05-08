# This script is designed to fetch IOCs (Indicators of Compromise) from a list of feed URLs, extract and normalize the IOCs, determine their types (IP or domain), calculate confidence scores based on the number of sources reporting each IOC, and save the results in both text and JSON formats. It also tracks the health of each feed and handles errors gracefully, logging any issues encountered during the fetching process.
import requests

# Import os and json for file handling, ipaddress for validating IPs, datetime for timestamps, and pathlib for path management
import os
import json
import ipaddress
from datetime import datetime, timezone, timedelta
from pathlib import Path
from utils.logger import logger

# Below is for path handling, ensuring it works regardless of where the script is run from
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
FEEDS_DIR = BASE_DIR / "feeds"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

#Below is for logging setup
feed_file = FEEDS_DIR / "urls.txt"

output_file = OUTPUT_DIR / "combined_iocs.txt"

json_output_file = OUTPUT_DIR / "combined_iocs.json"

feed_health_file = OUTPUT_DIR / "feed_health.json"

#Below is the function that checks if a given value is a valid IP address, ensuring it is not private, loopback, multicast, or reserved, which helps in filtering out non-relevant IPs from the feeds.
def is_valid_ip(value):

    try:

        ip = ipaddress.ip_address(value)

        if ip.is_private:
            return False

        if ip.is_loopback:
            return False

        if ip.is_multicast:
            return False

        if ip.is_reserved:
            return False

        return True

    except ValueError:

        return False

#Below is the function that checks if a given value is a valid domain name, ensuring it doesn't contain spaces, URLs, or other invalid characters, and that it has a reasonable length.
def is_valid_domain(value):

    value = value.strip().lower()

    if not value:
        return False

    if " " in value or "\t" in value:
        return False

    if value.startswith("#"):
        return False

    if value.startswith("http"):
        return False

    if "/" in value:
        return False

    if ":" in value:
        return False

    if "." not in value:
        return False

    if len(value) > 253:
        return False

    return True

#Below is the function that determines the type of IOC (IP or domain) based on the value, using the validation functions defined earlier.
def get_ioc_type(value):

    if is_valid_ip(value):
        return "ip"

    if is_valid_domain(value):
        return "domain"

    return None

# Below is the function that normalizes IOC values by stripping whitespace, converting to lowercase, and removing any extraneous data after tabs, ensuring that the IOCs are in a consistent format for processing and deduplication.
def normalize_ioc(value):

    value = value.strip().lower()

    if "\t" in value:
        value = value.split("\t")[0]

    return value

# Below is the function that checks if an IOC is expired based on its last seen timestamp, comparing it to the current time and a defined expiration period (e.g., 30 days), which helps in maintaining the relevance of the IOCs in the dataset.
def is_expired(last_seen):

    last_seen_time = datetime.fromisoformat(last_seen)

    expiration_time = last_seen_time + timedelta(days=IOC_EXPIRATION_DAYS)

    return datetime.now(timezone.utc) > expiration_time

#Below is the function that calculates a confidence score for an IOC based on the number of unique sources that have reported it, assigning higher confidence to IOCs that are seen in multiple feeds, which can help prioritize which IOCs to investigate further.
def calculate_confidence(source_count):

    if source_count >= 4:
        return 95

    if source_count == 3:
        return 80

    if source_count == 2:
        return 60

    return 40


all_iocs = set()
ioc_objects = {}
current_time = datetime.now(timezone.utc).isoformat()
IOC_EXPIRATION_DAYS = 30

# Below is the initialization of the main data structures: a set to store unique IOCs and a dictionary to store detailed information about each IOC, including its sources, type, confidence score, and timestamps for when it was first and last seen.
feed_health = {}

with open(feed_file, "r") as f:
    urls = [line.strip() for line in f if line.strip()]

#Below is the main loop that iterates through each feed URL, attempts to fetch the content, and processes each line to extract IOCs. It handles network errors and unexpected exceptions gracefully, logging any issues and updating the feed health status accordingly.
for url in urls:

    try:
        feed_ioc_count = 0
        source_url = url
        source_label = Path(url).stem

        logger.info(f"Fetching {url}")

# Below is the code that fetches the feed content, checks for errors, and processes each line to extract IOCs and update the metadata.
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        for line in response.text.splitlines():

            line = normalize_ioc(line)

            ioc_type = get_ioc_type(line)

            if ioc_type:

                all_iocs.add(line)
                feed_ioc_count += 1

                if line not in ioc_objects:
                    
                    ioc_objects[line] = {
                        "ioc": line,
                        "sources": [
                           {
                                "label": source_label,
                                "url": source_url
                            }
                    ],
                        "type": ioc_type,
                        "confidence": calculate_confidence(1),
                        "first_seen": current_time,
                        "last_seen": current_time,
                        "expired": False
                    }

                else:

#Below is the code that updates existing IOC entries with new sources, refreshes the last seen timestamp, checks for expiration, and recalculates the confidence score based on the number of unique sources reporting the IOC.
                    existing_labels = [
                        source["label"]
                        for source in ioc_objects[line]["sources"]
                    ]

                    if source_label not in existing_labels:

                        ioc_objects[line]["last_seen"] = current_time

                        ioc_objects[line]["expired"] = is_expired(
                            ioc_objects[line]["last_seen"]
                        )

                        ioc_objects[line]["sources"].append(
                            {
                                "label": source_label,
                                "url": source_url
                            }
                        )

                        source_count = len(ioc_objects[line]["sources"])

                        ioc_objects[line]["confidence"] = calculate_confidence(source_count)
                   

        feed_health[url] = {
            "status": "healthy",
            "ioc_count": feed_ioc_count
        }
    except requests.exceptions.RequestException as e:

        logger.error(f"Network failure processing feed: {url} | Error: {e}")

        print(f"[NETWORK ERROR] {url} | {e}")

        feed_health[url] = {
            "status": "failed",
            "ioc_count": 0,
            "error": str(e)
        }

    except Exception as e:

        logger.error(f"Unexpected failure processing feed: {url} | Error: {e}")

        print(f"[UNEXPECTED ERROR] {url} | {e}")

        feed_health[url] = {
            "status": "failed",
            "ioc_count": 0,
            "error": str(e)
        }
with open(output_file, "w") as f:
    for ioc in sorted(all_iocs):
        f.write(ioc + "\n")
with open(json_output_file, "w") as f:
    json.dump(list(ioc_objects.values()), f, indent=4)

with open(feed_health_file, "w") as f:
    json.dump(feed_health, f, indent=4)

print(f"[+] Saved {len(all_iocs)} IOCs")