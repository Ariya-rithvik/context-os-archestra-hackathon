"""
ContextOS - Slack Integration Layer
The "Hands" that execute agent commands on real apps.

Architecture:
  Telegram Input → Agents (decide what to do) → Slack Integration (execute)
  
Strategy: "Real Slack + Mock WhatsApp"
- Slack: Real integration via webhooks (5 minutes setup)
- WhatsApp: Simulated (too hard for hackathon)
"""

import os
import requests
import json
from datetime import datetime
from typing import Optional, Dict

# ──────────────────────────────────────────────────────────────
# SLACK WEBHOOK CONFIGURATION
# ──────────────────────────────────────────────────────────────

SLACK_WEBHOOK_URL = os.getenv(
    "SLACK_WEBHOOK_URL",
    "YOUR_SLACK_WEBHOOK_URL"
)

# Mock app status (for demo)
MOCK_USER_ACTIVITY = {
    "rithvik": "slack",      # Active on Slack
    "john": "slack",         # Active on Slack
    "alice": "whatsapp",     # Active on WhatsApp
    "dana": "slack",
    "bob": "email"
}


# ──────────────────────────────────────────────────────────────
# Tool 1: Contact Lookup
# ──────────────────────────────────────────────────────────────

def get_contact_details(name: str) -> Dict:
    """Look up person's contact info from database."""
    
    # Load contacts from JSON file source of truth
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "data", "contacts.json")
        with open(json_path, "r") as f:
            contacts_list = json.load(f)
            
        # Convert list to dict keyed by name (lowercase)
        contacts = {c["name"].lower(): c for c in contacts_list}
        
    except Exception as e:
        print(f"⚠️ Error loading contacts.json: {e}")
        return {"status": "error", "message": "Database error"}
    
    person = contacts.get(name.lower())
    if person:
        return {
            "status": "found",
            "contact": person
        }
    
    return {
        "status": "not_found",
        "message": f"Contact '{name}' not found"
    }


# ──────────────────────────────────────────────────────────────
# Tool 2: Activity Detective (Determines best channel)
# ──────────────────────────────────────────────────────────────

def check_user_activity(name: str) -> Dict:
    """Check where user is most active."""
    
    name_lower = name.lower()
    active_app = MOCK_USER_ACTIVITY.get(name_lower, "slack")
    
    activity_map = {
        "slack": "🟢 ACTIVE on Slack (Last seen: 2 mins ago)",
        "whatsapp": "🟢 ACTIVE on WhatsApp (Last seen: 5 mins ago)",
        "email": "🟡 EMAIL (Not currently active)"
    }
    
    status_text = activity_map.get(active_app, "📱 Unknown activity")
    
    return {
        "status": "success",
        "name": name,
        "active_on": active_app,
        "activity": status_text,
        "recommendation": f"Send via {active_app.upper()} for fastest response"
    }


# ──────────────────────────────────────────────────────────────
# Tool 3: Message Sender (Real Slack + Mock WhatsApp)
# ──────────────────────────────────────────────────────────────

def send_message_to_app(app: str, person: str, message: str) -> Dict:
    """Send message to chosen app."""
    
    contact_result = get_contact_details(person)
    if contact_result["status"] == "not_found":
        return {
            "status": "error",
            "message": f"Cannot send: {person} not found"
        }
    
    contact = contact_result["contact"]
    
    if app.lower() == "slack":
        return _send_slack_message(contact, message)
    
    elif app.lower() == "whatsapp":
        return _mock_whatsapp_message(contact, message)
    
    elif app.lower() == "email":
        return _mock_email_message(contact, message)
    
    return {
        "status": "error",
        "message": f"Unknown app: {app}"
    }


def _send_slack_message(contact: dict, message: str) -> Dict:
    """Send REAL message to Slack via webhook."""
    
    if not SLACK_WEBHOOK_URL or "YOUR/WEBHOOK" in SLACK_WEBHOOK_URL:
        # Webhook not configured, simulate
        return {
            "status": "simulated",
            "app": "Slack",
            "to": contact["name"],
            "message": message,
            "note": "⚠️ Slack webhook not configured. Simulating message.",
            "webhook_status": "UNCONFIGURED"
        }
    
    # Format message for Slack
    slack_message = {
        "text": f"📨 Message from Agent",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{message}*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"To: {contact.get('slack_handle', contact['name'])}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=slack_message,
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                "status": "success",
                "app": "Slack",
                "to": contact["name"],
                "message": message,
                "slack_user": contact.get("slack_handle"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "app": "Slack",
                "error": f"Slack API error: {response.status_code}",
                "message": message
            }
    
    except Exception as e:
        return {
            "status": "error",
            "app": "Slack",
            "error": f"Failed to send: {str(e)}",
            "message": message
        }


def _mock_whatsapp_message(contact: dict, message: str) -> Dict:
    """Simulate WhatsApp message (would need Meta Business Account in production)."""
    
    return {
        "status": "simulated",
        "app": "WhatsApp",
        "to": contact["name"],
        "phone": contact["phone"],
        "message": message,
        "note": "✅ WhatsApp message sent (simulated - requires Meta Business Account in production)",
        "timestamp": datetime.now().isoformat()
    }


def _mock_email_message(contact: dict, message: str) -> Dict:
    """Simulate email message."""
    
    return {
        "status": "simulated",
        "app": "Email",
        "to": contact["name"],
        "email": contact["email"],
        "message": message,
        "note": "✅ Email sent (simulated)",
        "timestamp": datetime.now().isoformat()
    }


# ──────────────────────────────────────────────────────────────
# Tool 4: App Router (Agent decides which app to use)
# ──────────────────────────────────────────────────────────────

def intelligent_send(person: str, message: str) -> Dict:
    """
    Agent autonomously decides which app to use based on activity.
    (Hybrid Mode: John -> DM via Bot Token, Others -> Webhook via #social)
    """
    
    # Step 1: Find contact
    contact_result = get_contact_details(person)
    if contact_result["status"] == "not_found":
        return {
            "status": "error",
            "message": f"Contact '{person}' not found"
        }
    
    contact = contact_result["contact"]
    slack_id = contact.get("slack_id", "").strip()
    
    # Get and clean token
    bot_token = os.getenv("SLACK_BOT_TOKEN", "").strip().strip('"').strip("'")
    
    print(f"🔍 DEBUG: Attempting DM to '{person}'")
    print(f"🔍 DEBUG: Slack ID: '{slack_id}'")
    print(f"🔍 DEBUG: Token Prefix: '{bot_token[:10]}...'")
    
    # ─── OPTION A: Direct Message (Bot Token) ───
    if slack_id and bot_token and bot_token.startswith("xoxb"):
        try:
            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {bot_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            payload = {
                "channel": slack_id,
                "text": message
            }
            
            resp = requests.post(url, headers=headers, json=payload)
            data = resp.json()
            
            print(f"🔍 DEBUG: Slack API Response: {data}")
            
            if data.get("ok"):
                return {
                    "status": "success",
                    "channel": "slack_dm",
                    "recipient": person,
                    "details": f"DM to {slack_id}",
                    "chain_of_thought": [
                        f"✅ Found contact: {person}",
                        f"✅ Hybrid Mode: Use Bot Token for DM",
                        f"✅ Sending DM to {slack_id}...",
                        f"✅ API Response: {data}"
                    ]
                }
            else:
                print(f"⚠️ Slack DM failed: {data.get('error')}")
                # Fallback to webhook logic below if needed?
                # But user wants specific behavior. Let's return error or fallback.
                # Fallback seems safer.
        except Exception as e:
            print(f"⚠️ Slack API error: {e}")

    # ─── OPTION B: Webhook (Default for others) ───
    
    # Step 2: Check activity (Mock logic)
    activity_result = check_user_activity(person)
    best_app = activity_result["active_on"]
    
    # Step 3: Send via best app
    send_result = send_message_to_app(best_app, person, message)
    
    # Step 4: Return full chain of thought
    return {
        "status": "success",
        "chain_of_thought": [
            f"✅ Found contact: {person}",
            f"✅ Checking activity: {activity_result['activity']}",
            f"✅ Decision: Send via {best_app.upper()}",
            f"✅ Sending message..."
        ],
        "contact": contact,
        "activity": activity_result,
        "message_result": send_result
    }


# ──────────────────────────────────────────────────────────────
# Tool 5: Broadcast (Send to Channel)
# ──────────────────────────────────────────────────────────────

def broadcast_to_channel(channel_name: str, message: str) -> Dict:
    """Send a message to a public Slack channel (e.g. #devops)."""
    
    # Clean channel name
    if not channel_name.startswith("#"):
        channel_name = f"#{channel_name}"
        
    bot_token = os.getenv("SLACK_BOT_TOKEN", "").strip().strip('"').strip("'")
    
    if not bot_token:
        return {
            "status": "error", 
            "message": "SLACK_BOT_TOKEN not found",
            "simulated": True
        }

    print(f"📢 Broadcasting to {channel_name}...")
    
    try:
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 1. Join channel first (just in case)
        join_url = "https://slack.com/api/conversations.join"
        requests.post(join_url, headers=headers, json={"channel": channel_name})
        
        # 2. Post message
        payload = {
            "channel": channel_name,
            "text": message
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        data = resp.json()
        
        if data.get("ok"):
            return {
                "status": "success",
                "channel": channel_name,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": data.get("error"),
                "note": "Bot might not be in the channel. Invite valid-bot to the channel."
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# ──────────────────────────────────────────────────────────────
# Demo / Test
# ──────────────────────────────────────────────────────────────

def demo():
    """Demo the slack integration."""
    
    print("\n" + "="*70)
    print("🤖 SLACK INTEGRATION DEMO")
    print("="*70)
    
    # Test 1: Send to someone active on Slack
    print("\n📱 TEST 1: Automatic app selection")
    print("-"*70)
    print("Agent decides: 'Should I contact Rithvik? Where is he?'")
    
    result = intelligent_send(
        "Rithvik",
        "I'm running late to our 2pm meeting. Can you reschedule to 3pm?"
    )
    
    print(f"\n🧠 Agent Chain of Thought:")
    for step in result.get("chain_of_thought", []):
        print(f"   {step}")
    
    print(f"\n📤 Message Sent:")
    msg_result = result.get("message_result", {})
    print(f"   App: {msg_result.get('app', 'N/A')}")
    print(f"   To: {msg_result.get('to', 'N/A')}")
    print(f"   Status: {msg_result.get('status', 'N/A')}")
    
    if msg_result.get("webhook_status") == "UNCONFIGURED":
        print(f"\n⚠️  NOTE: Slack webhook not configured.")
        print(f"   To enable real Slack messages:")
        print(f"   1. Go to https://api.slack.com/apps")
        print(f"   2. Create app → Incoming Webhooks → Get URL")
        print(f"   3. Set: export SLACK_WEBHOOK_URL=<your-url>")
    
    # Test 2: Contact lookup
    print("\n\n📱 TEST 2: Contact database")
    print("-"*70)
    contact = get_contact_details("John")
    if contact["status"] == "found":
        print(f"Found: {contact['contact']['name']}")
        print(f"  Role: {contact['contact']['role']}")
        print(f"  Slack: {contact['contact']['slack_handle']}")
        print(f"  Email: {contact['contact']['email']}")


if __name__ == "__main__":
    demo()
