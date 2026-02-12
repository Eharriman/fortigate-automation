import requests
import os
import urllib3
import json
from dotenv import load_dotenv

# Script initialization
load_dotenv()
FGT_FQDN = os.getenv("FGT_SB_FQDN")
API_KEY = os.getenv("FGT_SB_KEY")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print(FGT_FQDN)
print(API_KEY)