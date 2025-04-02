#!/bin/bash

echo "🚀 Starting Cybersecurity Application..."
source venv/bin/activate

echo "🛡️ Enforcing Zero-Trust Security..."
sudo python3 firewall.py &  # Background process

sleep 2  # Let firewall rules apply

echo "📡 Launching Continuous Monitoring..."
python3 simple_ui.py
