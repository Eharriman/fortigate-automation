import requests
import os
import urllib3
import json
from dotenv import load_dotenv

# --- SETUP ---
# Load environment variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

# Config
FQDN = os.getenv("FGT_SB_FQDN")
PORT = os.getenv("FGT_SB_PORT", "444")
API_KEY = os.getenv("FGT_SB_KEY")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probe_endpoint(name, url_suffix, params=None):
    """Helper to test a specific URL"""
    full_url = f"https://{FQDN}:{PORT}/api/v2{url_suffix}"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    
    try:
        print(f"[-] Probing {name}...")
        response = requests.get(full_url, headers=headers, params=params, verify=False, timeout=5)
        
        if response.status_code == 200:
            print(f"    [SUCCESS] Found! (Status 200)")
            return True
        elif response.status_code == 404:
            print(f"    [FAIL] 404 Not Found")
        elif response.status_code == 403:
            print(f"    [FAIL] 403 Forbidden (Check Admin Profile Permissions!)")
        elif response.status_code == 401:
            print(f"    [FAIL] 401 Unauthorized (Check API Key)")
        else:
            print(f"    [FAIL] Status {response.status_code}")
            
    except Exception as e:
        print(f"    [ERROR] Connection failed: {e}")
    
    return False

def run_diagnostics():
    print(f"--- DIAGNOSTIC MODE: {FQDN} ---\n")

    # TEST 1: System Status (Checks basic connectivity + VDOMs)
    # This almost ALWAYS works if the key is valid.
    print("1. CHECKING SYSTEM STATUS")
    url = f"https://{FQDN}:{PORT}/api/v2/monitor/system/status"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            fw_ver = data.get('version', 'Unknown')
            vdom_status = data.get('vdom', False)
            print(f"    [INFO] Firmware: {fw_ver}")
            print(f"    [INFO] VDOMs Enabled: {vdom_status}")
            
            # If VDOMs are enabled, this is likely the 404 cause
            if vdom_status:
                print("    [ALERT] VDOMs are ENABLED. You may need to specify '?vdom=root' in your URL.")
        else:
            print(f"    [CRITICAL] Basic System Status failed: {resp.status_code}")
            return
    except Exception as e:
        print(f"    [CRITICAL] Could not connect at all: {e}")
        return

    print("\n2. PROBING LOG PATHS")
    # Try the most common paths
    paths_to_try = [
        ("/log/disk/event", "Standard Disk Event"),
        ("/log/memory/event", "Standard Memory Event"),
        ("/log/disk/traffic", "Standard Disk Traffic"),
        ("/monitor/log/disk", "Monitor Path (Rare)"),
        ("/cmdb/log.disk/setting", "Log Disk Settings (Config Check)")
    ]

    found_path = False
    for path, name in paths_to_try:
        # We try to fetch just 1 item to verify access
        if probe_endpoint(name, path, params={'count': 1}):
            found_path = True

    print("\n3. VDOM TEST (If enabled)")
    # Explicitly try accessing the root VDOM
    probe_endpoint("Root VDOM Explicit", "/log/disk/event", params={'vdom': 'root', 'count': 1})

if __name__ == "__main__":
    run_diagnostics()