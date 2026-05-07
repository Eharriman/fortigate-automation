import requests
import os
import urllib3
import json
from dotenv import load_dotenv

# --- SETUP ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

FQDN = os.getenv("FGT_DR-UK_FQDN")
PORT = os.getenv("FGT_DR-UK_PORT", "443")
API_KEY = os.getenv("FGT_DR-UK_KEY")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_working_log_path():
    print(f"--- SEARCHING FOR LOGS ON {FQDN} ---")
    
    headers = {'Authorization': f'Bearer {API_KEY}'}
    base_url = f"https://{FQDN}:{PORT}/api/v2"

    # STEP 1: Get List of VDOMs
    # If this fails, the API user might be restricted to a single VDOM already.
    print("\n1. Fetching VDOM List...")
    vdom_url = f"{base_url}/cmdb/system/vdom"
    vdom_list = ["root"] # Default fallback
    
    try:
        resp = requests.get(vdom_url, headers=headers, verify=False, timeout=5, params={'vdom': 'root'})
        if resp.status_code == 200:
            data = resp.json()
            # Extract VDOM names
            if 'results' in data:
                vdom_list = [v['name'] for v in data['results']]
                print(f"   [SUCCESS] Found VDOMs: {vdom_list}")
            else:
                print("   [INFO] No VDOM results returned. Assuming 'root'.")
        else:
            print(f"   [WARN] Could not list VDOMs (Status {resp.status_code}). Trying 'root' only.")
            
    except Exception as e:
        print(f"   [ERROR] Connection failed: {e}")
        return

    # STEP 2: Probe Log API for each VDOM
    print("\n2. Probing Log Endpoints...")
    
    # We will try both 'disk' and 'memory' for each VDOM
    log_types = ['disk', 'memory']
    
    for vdom in vdom_list:
        for ltype in log_types:
            # Construct URL with explicit VDOM parameter
            test_url = f"{base_url}/log/{ltype}/event"
            params = {
                'vdom': vdom,
                'count': 1,
                'filter': 'subtype==vpn' # Only ask for VPN logs
            }
            
            print(f"   [-] Trying VDOM: '{vdom}' | Source: '{ltype}' ... ", end='')
            
            try:
                # We specifically pass the VDOM as a parameter
                log_resp = requests.get(test_url, headers=headers, params=params, verify=False, timeout=5)
                
                if log_resp.status_code == 200:
                    print(f"✅ SUCCESS!")
                    print(f"       -> URL: {test_url}?vdom={vdom}")
                    
                    data = log_resp.json()
                    results = data.get('results', [])
                    print(f"       -> Records Found: {len(results)}")
                    if results:
                        print(f"       -> Sample User: {results[0].get('user', 'N/A')}")
                        return # We found it! Stop searching.
                
                elif log_resp.status_code == 404:
                    print(f"❌ 404 (Not Found)")
                else:
                    print(f"❌ {log_resp.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Error: {e}")

    print("\n[SUMMARY] If all attempts failed with 404, verify that the API Admin User is not 'Restricted to VDOM' in System > Administrators.")

if __name__ == "__main__":
    find_working_log_path()