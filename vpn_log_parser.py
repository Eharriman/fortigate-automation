import re
import os
import ipaddress

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

    unique_bad_ips = set()

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

                    try:
                        ipaddress.ip_address(src_ip)
                        unique_bad_ips.add(src_ip)
                    except ValueError:
                        print(f"Warning: Invalid IP found in logs: {src_ip}")
                    else:
                        # Random attacks (no match)
                        random_attacks.append(username)   

                    #print(targeted_attacks)

    except FileNotFoundError:
        print("Could not find VPN log file. Check dir path")
        return
    
    #print("Detected attacks are: ", targeted_attacks)
    #print("Random attacks are: ", random_attacks)
    #return data
    print(f"Total Failed Attempts Found: {len(targeted_attacks) + len(random_attacks)}")
    print(f"Random Dictionary Attacks (Ignored): {len(random_attacks)}")
    print(f"Targeted Attacks (Concern): {len(targeted_attacks)}\n")

    if targeted_attacks:
        print("******** TARGETED ATTACKS REPORT ********")
        print(f"{'USER':<15} {'IP ADDRESS':<20} {'TIME':<10}")
        print("-" * 50)
        for attack in targeted_attacks:
            print(f"{attack['user']:<15} {attack['ip']:<20} {attack['time']:<10}")

        print(f"\nUnique IPs identified for blocking: {len(unique_bad_ips)}")

if __name__ == "__main__":
    print(analyze_logs())


