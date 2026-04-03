##########
# NOTICE #
##########
#
# This script is provided "as-is". I do not work for Cloudflare.
# I don't even have a paid account - I simply use their free service and needed
#   DDNS capabilities which did not appear to be supported through other means.
# I have done my best to write this in a way that I am comfortable using it
#    myself, but I'm nothing more than someone with a keyboard and
#   some coding knowledge.
# As such, use this at your own risk. Read and understand the code below.
#   I've tried to comment this as best as I can to ensure it can be understood
#   what my intent was on each line
# Cloudflare API Reference: https://api.cloudflare.com
##########

import json
import socket
import sys

import requests
from urllib3.util.connection import allowed_gai_family

# Force IPv4 — IPv6 DNS entries resolve but connections hang
requests.packages.urllib3.util.connection.allowed_gai_family = lambda: socket.AF_INET

# Check arguments
if len(sys.argv) > 3:
    raise AttributeError("Only 2 arguments to this script are supported!")

# Open the JSON-formatted parameters file and load it in to a Dict
with open(sys.argv[1]) as f:
    params = json.load(f)

# These are headers we'll have to send along with any of our requests
headers = {"X-Auth-Key":params['key'],"X-Auth-Email":params["email"],"Content-Type":"application/json"}

# Get public IP for non-Tailscale domains
public_ip = requests.get('https://api.ipify.org').text
# Get Tailscale IP from command line argument if provided and not empty
tailscale_ip = sys.argv[2] if len(sys.argv) == 3 and sys.argv[2].strip() else None

for domain in params['domains']:
    # Skip Tailscale domains if no Tailscale IP is available
    if domain['name'].endswith('.ts.chis.dev'):
        if not tailscale_ip:
            print(f"Skipping {domain['name']}: No Tailscale IP available")
            continue
        use_ip = tailscale_ip
        print(f"Updating {domain['name']} with Tailscale IP: {use_ip}")
    else:
        use_ip = public_ip
        print(f"Updating {domain['name']} with Public IP: {use_ip}")
        
    # Get record ID
    args = {"type":"A","name":domain['name']}
    r = requests.get(f"https://api.cloudflare.com/client/v4/zones/{params['zone']}/dns_records", headers=headers, params=args)
    recordid = r.json()['result'][0]['id']

    # Update record
    args = {"type":"A","name":domain['name'],"content":use_ip,"ttl":1,'proxied':domain['proxied']}
    p = requests.put(f"https://api.cloudflare.com/client/v4/zones/{params['zone']}/dns_records/{recordid}",
                    headers=headers, data=json.dumps(args))
    print(f"Response for {domain['name']}: {p.status_code}")
