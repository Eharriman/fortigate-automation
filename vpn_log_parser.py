import re
import os
import ipaddress
import csv
from datetime import datetime
from dotenv import load_dotenv

# Static 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, "vpn_log_files")
LOG_FILE = os.path.join(SCRIPT_DIR, "sample_vpn_log.txt")
USER_LIST = os.path.join(SCRIPT_DIR, "valid_users.csv")
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")

# ENV variables
load_dotenv(ENV_FILE)
author = os.getenv('AUTHOR')
VALID_DOMAINS = os.getenv('VALID_DOMAINS')


#VALID_USER_DICT = {"marvin","martin", "jsmith", "bwayne"}

def load_users_from_csv(filepath):

    valid_users = set()

    if not os.path.exists(filepath):
        print(f"[ERROR] User DB file not found: {filepath}")
        return valid_users

    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # normalize to lowercase for consistent matching
                if 'username' in row and row['username']:
                    valid_users.add(row['username'].strip().lower())
                    
        print(f"[INFO] Loaded {len(valid_users)} users from CSV.")
    except Exception as e:
        print(f"[ERROR] Failed to read user CSV: {e}")
        
    return valid_users

# Load users
VALID_USER_SET = load_users_from_csv(USER_LIST)

def parse_log_line(line):
    # regex
    pattern = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]+)"|(\S+))')

    log_dict = {}

    for match in pattern.finditer(line):
        key = match.group(1)
        uid = match.group(2) if match.group(2) is not None else match.group(3)
        log_dict[key] = uid
    
    return log_dict


def generate_block_addr(ip_list):

    if not ip_list:
        print("No IPs in set")
        return
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"conf_add_ips_blocked_ssl-vpn_{date_str}.conf"
    filepath = os.path.join(SCRIPT_DIR, filename)

    try:
        with open(filepath, "w") as f:
            f.write(f"# Automated block SSL-VPN Script\n")
            f.write(f"# Date: {date_str}\n")
            f.write(f"# Executor: {author}\n")
            f.write(f"# Total IPs: {len(ip_list)}\n\n")

            # Create address objects based on unique IPs
            f.write("config firewall address\n")
            for ip in ip_list:
                obj_name = f"Blocked_SSL_VPN_IP_{ip}"
                f.write(f'    edit "{obj_name}"\n')
                f.write(f'        set subnet {ip} 255.255.255.255\n')
                f.write(f'        set comment "Targeted Attack Block {date_str}"\n')
                f.write('    next\n')
            f.write("end\n\n")

           # Add address objects to addr group
            f.write("config firewall addrgrp\n")
            f.write('    edit "Blocked_SSL_VPN_List"\n')
            for ip in ip_list:
                obj_name = f"Blocked_SSL_VPN_IP_{ip}"
                f.write(f'        append member "{obj_name}"\n')
            f.write('    next\n')
            f.write("end\n")

        print(f"\n[SUCCESS] Configuration saved to:\n -> {filepath}")

    except Exception as e:
        print(f"\n [ERROR] failed to write to conf file: {e}")


def is_targeted_attack(username):

    user_lower = username.lower()

    if user_lower in VALID_USER_SET:
        return True
    
    if "@" in user_lower:
        try:
            domain_part = user_lower.split("@")[1]
            if domain_part in VALID_DOMAINS:
                return True
            
        except IndexError:
            pass

    return False


def generate_csv_report(attack_list):

    if not attack_list:
        print("No targeted attacks found")
        return
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"ssl-vpn_attack_report_{date_str}.csv"
    filepath = os.path.join(SCRIPT_DIR, filename)

    headers = ['User', 'Source IP', 'Time', 'Reason']

    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader

            for attack in attack_list:
                writer.writerow({
                    'User': attack.get('user'),
                    'Source IP': attack.get('ip'),
                    'Time': attack.get('time'),
                    'Reason': attack.get('reason')
                })
    except Exception as e:
        print(f"[Error] is writing to csv file: {e}")


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

                    #if username in VALID_USER_DICT:
                    if is_targeted_attack(username):
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

    # Generate report and conf script
    if targeted_attacks:
        print(f"\nUnique IPs identified for blocking: {len(unique_bad_ips)}")
        generate_csv_report(targeted_attacks)
        generate_block_addr(unique_bad_ips)

if __name__ == "__main__":
    print(analyze_logs())


