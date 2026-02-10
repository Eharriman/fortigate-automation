import os
import requests
from dotenv import load_dotenv

load_dotenv()

FGT_FQDN = os.getenv("FGT_SB_FQDN")
FGT_PORT = os.getenv("FGT_SB_PORT")
API_KEY = os.getenv("FGT_SB_KEY")

def get_policy(policy_id)