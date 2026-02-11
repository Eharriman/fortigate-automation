import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "sample_vpn_log.txt")
#LOG_File = "sample_vpn_log.txt"

VALID_USER_DICT = {"marvin","martin", "jsmith", "bwayne"}

def parse_log_line(line):
    # regex
    pattern = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]+)"|(\S+))')

    log_dict = {}

    for match in pattern.finditer(line):
        key = match.group(1)
        uid = match.group(2) if match.group(2) is not None else match.group(3)
        log_dict[key] = uid
    
    return log_dict



def analyze_logs():
    #Initialize lists
    targeted_attacks = []
    random_noise = []

    # Main log analysis
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
            data = parse_log_line(line)
    
    except FileNotFoundError:
        print("Could not find VPN log file. Check dir path")
        return
    
    return data


if __name__ == "__main__":
    print(analyze_logs())


