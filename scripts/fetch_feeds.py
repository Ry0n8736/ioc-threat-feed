import requests
from pathlib import Path

feed_file = Path("../feeds/urls.txt")
output_file = Path("../output/combined_iocs.txt")

all_iocs = set()

with open(feed_file, "r") as f:
    urls = [line.strip() for line in f if line.strip()]

for url in urls:
    print(f"[+] Fetching {url}")

    response = requests.get(url, timeout=20)

    for line in response.text.splitlines():

        line = line.strip()

        if (
            line
            and not line.startswith("#")
            and "." in line
        ):
            all_iocs.add(line)

with open(output_file, "w") as f:
    for ioc in sorted(all_iocs):
        f.write(ioc + "\n")

print(f"[+] Saved {len(all_iocs)} IOCs")