import os
import requests

# Load .env manually to get token
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_file = os.path.join(project_root, ".env")
print(f"📂 Looking for .env at: {env_file}")

token = None
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key == "SLACK_BOT_TOKEN":
                    token = value
                    break

if not token:
    print("❌ SLACK_BOT_TOKEN not found in .env")
    exit(1)

print(f"🔑 Using Token: {token[:10]}...")

url = "https://slack.com/api/users.list"
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if not data.get("ok"):
        print(f"❌ Error: {data.get('error')}")
        exit(1)
        
    print("\n👥 Slack Users Found:")
    print("-" * 50)
    print(f"{'ID':<12} | {'Real Name':<20} | {'Name':<15} | {'Is Bot'}")
    print("-" * 50)
    
    for member in data.get("members", []):
        if member.get("deleted"): continue
        uid = member.get("id")
        real_name = member.get("real_name", "N/A")
        name = member.get("name", "N/A")
        is_bot = member.get("is_bot", False)
        
        print(f"{uid:<12} | {real_name:<20} | {name:<15} | {is_bot}")

    print("-" * 50)
    print("✅ Copy the ID of the user you want to masquerade as 'John'.")

except Exception as e:
    print(f"❌ Exception: {e}")
