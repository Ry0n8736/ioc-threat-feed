import requests
import os
import json
import ipaddress
from datetime import datetime, timezone
from pathlib import Path
from utils.logger import logger

feed_file = Path("feeds/urls.txt")
output_file = Path("output/combined_iocs.txt")
json_output_file = Path("output/combined_iocs.json")

def is_valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_valid_domain(value):

    if " " in value:
        return False

    if value.startswith("#"):
        return False

    if value.startswith("http"):
        return False

    if "." not in value:
        return False

    return True

def get_ioc_type(value):

    if is_valid_ip(value):
        return "ip"

    if is_valid_domain(value):
        return "domain"

    return None


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

with open(feed_file, "r") as f:
    urls = [line.strip() for line in f if line.strip()]

for url in urls:
    source_name = url.split("/")[2]
    logger.info(f"Fetching {url}")

    response = requests.get(url, timeout=20)

    for line in response.text.splitlines():

        line = line.strip()

        ioc_type = get_ioc_type(line)

        if ioc_type:

            all_iocs.add(line)

            if line not in ioc_objects:

                 ioc_objects[line] = {
                    "ioc": line,
                    "sources": [source_name],
                    "type": ioc_type,
                    "confidence": calculate_confidence(1),
                    "first_seen": current_time,
                    "last_seen": current_time
                }

            else:

                if source_name not in ioc_objects[line]["sources"]:
                    ioc_objects[line]["sources"].append(source_name)
                    source_count = len(ioc_objects[line]["sources"])

                    ioc_objects[line]["confidence"] = calculate_confidence(source_count)
                    ioc_objects[line]["last_seen"] = current_time
with open(output_file, "w") as f:
    for ioc in sorted(all_iocs):
        f.write(ioc + "\n")
with open(json_output_file, "w") as f:
  json.dump(list(ioc_objects.values()), f, indent=4)
print(f"[+] Saved {len(all_iocs)} IOCs")