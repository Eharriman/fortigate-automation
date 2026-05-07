import os
import re
import csv
from datetime import datetime

# --- CONFIGURATION ---
# ROOT_DIR dynamically finds where this python script is located
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Directory Definitions
EXTERNAL_DIR = os.path.join(ROOT_DIR, "external")
GEN_DIR = os.path.join(ROOT_DIR, "Generated Scripts")

# File Definitions
CSV_FILE = os.path.join(EXTERNAL_DIR, "gateway_ips.csv")
CONF_FILE = os.path.join(EXTERNAL_DIR, "fw_address.conf")

def get_existing_ips(conf_path):
    """
    Parses the FortiGate conf excerpt and returns a set of all IPs
    found in 'set subnet <IP> <Mask>' lines.
    """
    existing_ips = set()
    if not os.path.exists(conf_path):
        print(f"[ERROR] Conf file not found at:\n -> {conf_path}")
        print("Please check the folder path and ensure Windows didn't add a hidden '.txt' extension.")
        return existing_ips

    # Regex looks for 'set subnet' followed by an IP address format
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
    """
    Reads the CSV and returns a list of tuples (IP, Site) 
    that are NOT present in the existing_ips set.
    """
    missing_gateways = []
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found at:\n -> {csv_path}")
        return missing_gateways

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

    print(f"[INFO] Found {len(missing_gateways)} missing IPs from the CSV.")
    return missing_gateways

def generate_missing_conf(missing_list):
    """
    Generates a FortiGate configuration script for the missing IPs.
    """
    if not missing_list:
        print("[SUCCESS] All IPs from the CSV are already in the FortiGate config!")
        return
        
    # Ensure the Generated Scripts directory exists
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

def main():
    print("--- Starting IP Cross-Reference ---")
    
    # 1. Parse the Config file for existing IPs
    existing_ips = get_existing_ips(CONF_FILE)
    if not existing_ips:
        return

    # 2. Check the CSV against the existing IPs
    missing_gateways = find_missing_gateways(CSV_FILE, existing_ips)
    
    # 3. Generate the script for any missing items
    if missing_gateways:
        generate_missing_conf(missing_gateways)

if __name__ == "__main__":
    main()