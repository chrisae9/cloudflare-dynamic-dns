#!/bin/bash
TAILSCALE_IP=$(docker exec tailscale tailscale ip --4 2>/dev/null || echo "")
/usr/bin/python3 /home/chis/www/cloudflare-dynamic-dns/raindrop.py /home/chis/www/cloudflare-dynamic-dns/credentials.json "$TAILSCALE_IP"
