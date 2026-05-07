import requests
import os
import urllib3
import json
from dotenv import load_dotenv

# --- SETUP ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

FQDN = os.getenv("FGT_SB_FQDN")
PORT = os.getenv("FGT_SB_PORT", "444")
API_KEY = os.getenv("FGT_SB_KEY")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_category(category_name):
    url = f"https://{FQDN}:{PORT}/api/v2/log/disk/{category_name}"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    params = {'count': 1, 'vdom': 'root'} # Minimal request
    
    print(f"[-] Testing Category: '{category_name}' ... ", end='')
    
    try:
        resp = requests.get(url, headers=headers, params=params, verify=False, timeout=5)
        if resp.status_code == 200:
            print(f"✅ SUCCESS (200 OK)")
            return True
        elif resp.status_code == 404:
            print(f"❌ FAILED (404 Not Found)")
        else:
            print(f"⚠️ STATUS {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return False

print(f"--- DIAGNOSING LOG CATEGORIES ON {FQDN} ---")
# Test the "Big Three" categories
test_category("traffic")  # Do forwarding logs work?
test_category("event")    # Do system/VPN logs work?
test_category("utm")      # Do security logs work?