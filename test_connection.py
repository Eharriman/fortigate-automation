import os
import requests
from dotenv import load_dotenv

load_dotenv()

FGT_FQDN = os.getenv("FGT_SB_FQDN")
FGT_PORT = os.getenv("FGT_SB_PORT")
API_KEY = os.getenv("FGT_SB_KEY")

#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url = f"https://{FGT_FQDN}:{FGT_PORT}/api/v2/monitor/system/status"
headers = {'Authorization': f'Bearer {API_KEY}'}


print(f"Connecting to {FGT_FQDN}...")
try:
    response = requests.get(url, headers=headers, verify=False, timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Firmware Version: {data['version']}")
    else:
        print(f"Failed: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")