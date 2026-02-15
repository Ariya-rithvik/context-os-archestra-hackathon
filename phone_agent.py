import os
import requests
import json
from typing import Dict, Any

class PhoneCallingAgent:
    """
    Agent capable of initiating real-world phone calls via Vapi.ai.
    """
    def __init__(self, message_bus=None, task_queue=None):
        self.message_bus = message_bus
        self.task_queue = task_queue
        self.api_key = os.getenv("VAPI_API_KEY")
        self.phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
        self.api_url = "https://api.vapi.ai/call/phone"

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a calling task.
        Expected task schema:
        {
            "action": "call",
            "number": "+1234567890",
            "goal": "Book a table for 2 at 7pm",
            "context": {...}
        }
        """
        if not self.api_key or not self.phone_number_id:
            return {
                "status": "error",
                "message": "❌ VAPI_API_KEY or VAPI_PHONE_NUMBER_ID not set in .env"
            }

        target_number = task.get("number")
        goal = task.get("goal", "Have a helpful conversation.")

        if not target_number:
            return {"status": "error", "message": "❌ No phone number provided"}

        # Construct Vapi Payload
        # We use the 'assistant-overrides' pattern to change the prompt dynamically
        # even if we are using a pre-configured Assistant ID.
        payload = {
            "assistant": {
                "transcriber": {
                    "provider": "deepgram",
                    "model": "nova-2",
                    "language": "en-US"
                },
                "model": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system", 
                            "content": f"You are a helpful assistant from ContextOS. Your goal is: {goal}. Be concise and polite."
                        }
                    ]
                },
                "firstMessage": f"Hello, I am calling about: {goal}.",
                "voice": {
                    "provider": "11labs",
                    "voiceId": "burt"
                }
            },
            "phoneNumberId": self.phone_number_id,
            "customer": {
                "number": target_number
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            print(f"📞 Calling {target_number}...")
            response = requests.post(self.api_url, headers=headers, json=payload)
            data = response.json()
            
            if response.status_code == 201:
                return {
                    "status": "success",
                    "message": f"✅ Call initiated to {target_number}",
                    "call_id": data.get("id"),
                    "steps": [
                        f"📞 Dialing {target_number}...",
                        f"🤖 AI Goal: '{goal}'",
                        f"✅ Call connected (ID: {data.get('id')})"
                    ]
                }
            else:
                return {
                    "status": "error",
                    "message": f"❌ Call failed: {data}",
                    "steps": [
                        f"📞 Dialing {target_number}...",
                        f"❌ API Error: {data}"
                    ]
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Exception: {e}",
                "steps": [f"❌ System Error: {e}"]
            }
