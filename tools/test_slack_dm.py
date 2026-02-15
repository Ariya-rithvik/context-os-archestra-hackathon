import os
import json
import requests

# 1. Load .env
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_file = os.path.join(project_root, ".env")
print(f"📂 Loading .env from: {env_file}")

token = None
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("SLACK_BOT_TOKEN="):
                token = line.split("=", 1)[1].strip('"').strip("'")
                break

if not token:
    print("❌ SLACK_BOT_TOKEN not found!")
    exit(1)

print(f"🔑 Token found: {token[:10]}...")

# 2. Get John's ID
contacts_file = os.path.join(project_root, "data", "contacts.json")
with open(contacts_file, "r") as f:
    contacts = json.load(f)

john_id = None
for c in contacts:
    if c.get("name") == "John":
        john_id = c.get("slack_id")
        break

if not john_id:
    print("❌ John's Slack ID not found in contacts.json")
    exit(1)

print(f"👤 Sending DM to John ({john_id})...")

# 3. Send DM
url = "https://slack.com/api/chat.postMessage"
headers = {"Authorization": f"Bearer {token}"}
payload = {
    "channel": john_id,
    "text": "🔔 Test DM from ContextOS Debugger. Can you see this?"
}

try:
    resp = requests.post(url, headers=headers, json=payload)
    data = resp.json()
    print(f"\n📡 API Response: {json.dumps(data, indent=2)}")
    
    if data.get("ok"):
        print("✅ SUCCESS! Message sent.")
    else:
        print(f"❌ FAILED! Error: {data.get('error')}")

except Exception as e:
    print(f"❌ Exception: {e}")
