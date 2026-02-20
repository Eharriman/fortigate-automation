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
        print(f"[ERROR] User DB file not found: {conf_path}")
        return existing_ips
    
    pass