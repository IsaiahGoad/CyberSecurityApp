import os

# Define trusted IPs (all others will be blocked)
TRUSTED_IPS = ["192.168.1.1", "10.0.0.5"]

def enforce_zero_trust(ip):
    """Blocks all non-trusted IPs."""
    if ip not in TRUSTED_IPS:
        print(f"🚫 Blocking Unauthorized IP: {ip}")
        os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")