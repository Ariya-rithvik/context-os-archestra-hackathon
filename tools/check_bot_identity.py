import os
import requests

# Load Token
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_file = os.path.join(project_root, ".env")

token = None
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.startswith("SLACK_BOT_TOKEN="):
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not token:
    print("❌ Token missing")
    exit(1)

# Call auth.test
url = "https://slack.com/api/auth.test"
headers = {"Authorization": f"Bearer {token}"}

try:
    resp = requests.post(url, headers=headers)
    data = resp.json()
    print(f"\n🤖 Bot Identity Check: {data}")
    
    if data.get("ok"):
        bot_id = data.get("bot_id")
        user_id = data.get("user_id")
        print(f"✅ Authenticated as Bot User ID: {user_id}")
        print(f"✅ Bot ID: {bot_id}")
    else:
        print(f"❌ Auth failed: {data.get('error')}")

except Exception as e:
    print(f"❌ Error: {e}")
