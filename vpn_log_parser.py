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
    random_attacks = []

    # Main log analysis
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = parse_log_line(line)

                # Log Description field 
                if data.get("logdesc") == "SSL VPN login fail":

                    username = data.get("user", "UKNOWN")
                    src_ip = data.get("remip", "0.0.0.0")

                    #print(username)
                    #print(src_ip)

                    if username in VALID_USER_DICT:
                        attack_record = {
                            "user": username,
                            "ip": src_ip,
                            "time": data.get("time"),
                            "reason": data.get("reason")                        
                        }
                        targeted_attacks.append(attack_record)
                    else:
                        # RANDOM NOISE
                        random_attacks.append(username)   

                    #print(targeted_attacks)

    except FileNotFoundError:
        print("Could not find VPN log file. Check dir path")
        return
    
    print("Detected attacks are: ", targeted_attacks)
    print("Random attacks are: ", random_attacks)
    #return data


if __name__ == "__main__":
    print(analyze_logs())


