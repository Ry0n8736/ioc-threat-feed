# This module is responsible for enriching the IOCs with intelligence data.
import json

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IOC_FILE = BASE_DIR / "output" / "combined_iocs.json"

# This class is responsible for enriching the IOCs with intelligence data.
class IOCIntelligence:
    def __init__(self):

        self.ioc_lookup = {}

        self.load_iocs()
        
    def load_iocs(self):

        with open(IOC_FILE, "r") as f:

            ioc_data = json.load(f)

        for entry in ioc_data:

            ioc_value = entry["ioc"]

            self.ioc_lookup[ioc_value] = entry