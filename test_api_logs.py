import requests
import os
import urllib3
import json
from dotenv import load_dotenv

# Script initialization
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dict for all FortiGates
current_device = {
    "name": "FortiGate-DR-UK",
    "fqdn": os.getenv("FGT_DR-UK_FQDN"),
    "port": os.getenv("FGT_DR-UK_PORT", "444"),
    "api_key": os.getenv("FGT_DR-UK_KEY")    
}

def get_vpn_logs(device):
    
    fqdn = device.get("fqdn")
    port = device.get("port")
    key = device.get("api_key")
    name = device.get("name")

    if not fqdn or not key:
        print(f"[Error] missing FQDN or API key for connection on FortiGate: {name}. Check .env variables")
        return
    
    #base_url = f"https://{fqdn}:{port}/api/v2/log/disk/event"
    base_url = f"https://{fqdn}:{port}/api/v2/log/memory/event"

    payload = {
        "filter": ["subtype==vpn", "action==ssl-login-fail"],
        "count": 5  # Limit to 5 for this test        
    }

    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'        
    }

    print(f"\n********** Connecting to {name} ({fqdn}:{port}) **********")

    try:
            response = requests.get(base_url, headers=headers, params=payload, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                print(f"[SUCCESS] Connection Established!")
                print(f"Logs Found: {len(results)}")
                
                if results:
                    print("Sample Entry keys:", list(results[0].keys()))
                    # Uncomment to see full raw JSON
                    # print(json.dumps(results[0], indent=2))
                else:
                    print("No recent SSL VPN failures found on this device.")

            elif response.status_code == 404:
                print(f"[ERROR 404] Endpoint not found.")
                print("Tip: If this is a smaller unit, try changing URL to '/api/v2/log/memory/event'")
                
            elif response.status_code == 401:
                print(f"[ERROR 401] Unauthorized. Check API Key permissions.")
                
            else:
                print(f"[ERROR] Status {response.status_code}: {response.text}")

    except Exception as e:
            print(f"[CRITICAL] Connection Failed: {e}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # In the future, this will be: for dev in device_list: fetch_vpn_logs(dev)
    get_vpn_logs(current_device)