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
    #pass

    missing_gateways = []

    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found at:\n -> {csv_path}")
        return 
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
                
            ip = row[0].strip()
            site = row[1].strip()
            
            # Skip header row if it exists
            if ip.lower() == 'ip':
                continue
                
            if ip not in existing_ips:
                missing_gateways.append((ip, site))

    return 

def generate_missing_conf(missing_list):

    if not missing_list:
        print("[SUCCESS] All IPs from the CSV are already in the FortiGate config!")
        
    os.makedirs(GEN_DIR, exist_ok=True)
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"conf_appgate_gateways_{date_str}.conf"
    filepath = os.path.join(GEN_DIR, filename)

    try:
        with open(filepath, "w") as f:
            f.write("# Automated AppGate GW Address Script\n")
            f.write(f"# Date: {date_str}\n")
            f.write(f"# Total Missing IPs to Add: {len(missing_list)}\n\n")

            f.write("config firewall address\n")
            for ip, site in missing_list:
                # Replace spaces in site name with underscores just in case
                safe_site_name = site.replace(" ", "_")
                obj_name = f"AppGate_GW-{safe_site_name}"
                
                f.write(f'    edit "{obj_name}"\n')
                f.write(f'        set subnet {ip} 255.255.255.255\n')
                f.write('    next\n')
            f.write("end\n")

        print(f"\n[SUCCESS] Configuration saved to:\n -> {filepath}")
    except Exception as e:
        print(f"[ERROR] Failed to write conf file: {e}")