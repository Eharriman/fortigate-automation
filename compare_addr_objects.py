import os
import re
import csv
from datetime import datetime

# Paths
# External place the conf addr current config for the FortiGate & current_ips.conf
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 
EXTERNAL_DIR = os.path.join(ROOT_DIR, "external")
GEN_DIR = os.path.join(ROOT_DIR, "Generated Scripts")

# File Definitions
CSV_FILE = os.path.join(EXTERNAL_DIR, "external_ips.csv")
CONF_FILE = os.path.join(EXTERNAL_DIR, "current_ips.conf")

def get_existing_ips(conf_path):
    # parses existing ips in current conf
    existing_ips = set()

    if not os.path.exists(conf_path):
        print(f"[ERROR] Conf file not found: {conf_path}")
        return existing_ips
    
    pattern = re.compile(r'^\s*set\s+subnet\s+([0-9\.]+)')

    with open(conf_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                ip = match.group(1)
                existing_ips.add(ip)

    print(f"{len(existing_ips)} found in conf file")


def get_missing_ips(csv_path, existing_ips):

    missing_ips = []

    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        return existing_ips
    
    # Identifies ips in subnet line of conf file
    pattern = re.compile(r'^\s*set\s+subnet\s+([0-9\.]+)')

    with open(conf_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                ip = match.group(1)
                existing_ips.add(ip)

    print(f"[INFO] Found {len(existing_ips)} unique IPs in the config excerpt.")
    return existing_ips

def find_missing_gateways(csv_path, existing_ips):
    pass