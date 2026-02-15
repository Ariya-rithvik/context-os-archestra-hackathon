"""
ContextOS — Telegram Integration Layer
The "WhatsApp-like" input node for the Semantic-RPC Bridge.

This is the "Universal Input Node" that connects to the semantic router.
Instead of building a website, this is an invisible AI service.

Setup:
  1. Get Telegram bot token: https://t.me/botfather → /newbot
  2. Export: set TELEGRAM_BOT_TOKEN=<your-token>
  3. Run: python telegram_bot.py

The bot will:
  • Listen for messages (text, voice, images)
  • Send to semantic router
  • Execute MCP tools
  • Reply with results

Architecture:
  Telegram User → telegram_bot.py → semantic_router.py → MCP Tools → data/*.json
"""

import os
import sys
import json
import uuid
import asyncio

from datetime import datetime
from typing import Optional

# Load .env manually BEFORE imports
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip().strip('"')

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from semantic_router import process_message
from multi_agent_system import AgentOrchestrator
from slack_integration import intelligent_send

# Try to import telegram library
try:
    from telegram import Update, Chat
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ContextTypes,
        filters,
    )
    from telegram.constants import ParseMode, ChatAction
except ImportError:
    print("❌ python-telegram-bot not installed!")
    print("   Run: pip install python-telegram-bot")
    sys.exit(1)

from voice_processor import VoiceProcessor



# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
    print("   Setup:")
    print("   1. Go to https://t.me/botfather")
    print("   2. Type /newbot and follow instructions")
    print("   3. Copy your token")
    print("   4. Run: set TELEGRAM_BOT_TOKEN=<your-token>")
    print("   5. Then: python telegram_bot.py")
    sys.exit(1)

# Optional: Slack webhook
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
if not SLACK_WEBHOOK_URL:
    print("⚠️  SLACK_WEBHOOK_URL not set. Agent messages will be simulated.")
    print("   To enable real Slack messages: set SLACK_WEBHOOK_URL=<your-url>")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Create temp_audio directory for voice messages
os.makedirs("temp_audio", exist_ok=True)

# Track conversations (user_id → context)
CONVERSATIONS = {}


# ──────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────
def _load_json(filename: str) -> list:
    """Load JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_json(filename: str, data: list) -> None:
    """Save to JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _gen_id(prefix: str) -> str:
    """Generate unique ID."""
    return f"{prefix}-{uuid.uuid4().hex[:4]}"


def _execute_rpc(rpc: dict) -> dict:
    """Execute a single RPC call (mimics MCP server behavior)."""
    tool = rpc["tool"]
    p = rpc["params"]
    now = datetime.now().isoformat()

    if tool == "schedule_event":
        eid = _gen_id("EVT")
        entry = {
            "id": eid,
            "topic": p.get("topic", ""),
            "time": p.get("time", ""),
            "participants": p.get("participants", []),
            "created_at": now,
            "status": "scheduled"
        }
        data = _load_json("calendar.json")
        data.append(entry)
        _save_json("calendar.json", data)
        return {
            "agent": "📅 Calendar",
            "action": "schedule_event",
            "id": eid,
            "message": f"Meeting '{p.get('topic', '')}' scheduled for {p.get('time', '')} with {', '.join(p.get('participants', []))}",
            "emoji": "📅"
        }

    elif tool == "trigger_alert":
        aid = _gen_id("ALT")
        entry = {
            "id": aid,
            "system": p.get("system", ""),
            "issue": p.get("issue", ""),
            "priority": p.get("priority", "Medium"),
            "created_at": now,
            "status": "active"
        }
        data = _load_json("alerts.json")
        data.append(entry)
        _save_json("alerts.json", data)
        return {
            "agent": "🚨 Alert",
            "action": "trigger_alert",
            "id": aid,
            "message": f"Alert sent for {p.get('system', '')} — {p.get('issue', '')} [{p.get('priority', '').upper()}]",
            "emoji": "🚨"
        }

    elif tool == "create_ticket":
        tid = _gen_id("TKT")
        entry = {
            "id": tid,
            "assignee": p.get("assignee", ""),
            "summary": p.get("summary", ""),
            "due": p.get("due", ""),
            "priority": p.get("priority", "Medium"),
            "created_at": now,
            "status": "open"
        }
        data = _load_json("tickets.json")
        data.append(entry)
        _save_json("tickets.json", data)
        return {
            "agent": "🎫 Ticket",
            "action": "create_ticket",
            "id": tid,
            "message": f"Ticket assigned to {p.get('assignee', '')}: '{p.get('summary', '')}' — due {p.get('due', '')}",
            "emoji": "🎫"
        }

    elif tool == "create_reminder":
        rid = _gen_id("REM")
        entry = {
            "id": rid,
            "message": p.get("message", ""),
            "time": p.get("time", ""),
            "target": p.get("target", ""),
            "created_at": now,
            "status": "pending"
        }
        data = _load_json("reminders.json")
        data.append(entry)
        _save_json("reminders.json", data)
        return {
            "agent": "⏰ Reminder",
            "action": "create_reminder",
            "id": rid,
            "message": f"Reminder set for {p.get('target', '')}: '{p.get('message', '')}' at {p.get('time', '')}",
            "emoji": "⏰"
        }

    return {
        "agent": "❓ Unknown",
        "action": tool,
        "id": "",
        "message": f"Unknown tool: {tool}",
        "emoji": "❓"
    }


# ──────────────────────────────────────────────────────────────
# Telegram Bot Class
# ──────────────────────────────────────────────────────────────
class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.orchestrator = AgentOrchestrator(telegram_bot=self)
        self.voice_processor = VoiceProcessor()
        # Use HTTPXRequest with HTTP/1.1 enforcement for stability
        from telegram.request import HTTPXRequest
        request = HTTPXRequest(
            connection_pool_size=10,
            connect_timeout=40.0,
            read_timeout=40.0,
            write_timeout=40.0,
            pool_timeout=40.0,
            http_version="1.1",  # Force HTTP/1.1 to avoid httpcore/http2 bugs
            keep_alive_timeout=20.0  # Recycle connections faster to avoid Stale/ConnectError
        )

        self.application = (
            Application.builder()
            .token(self.token)
            .request(request)
            .get_updates_request(request)
            .build()
        )

        # Handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Add global error handler
        self.application.add_error_handler(self.error_handler)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        
        # If it's a network error, just sleep and return (don't crash)
        if "ConnectError" in str(context.error) or "NetworkError" in str(context.error):
            print(f"⚠️ Network error detected: {context.error}. Sleeping for 5s before retrying...")
            await asyncio.sleep(5)
            return

        print(f"🔥 Exception while handling an update: {context.error}")
        import traceback
        traceback.print_exc()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name

        welcome = (
            f"⚡ Welcome to ContextOS, {user_name}!\n\n"
            "I'm your Semantic-RPC Bridge. Send me natural language commands and I'll execute them.\n\n"
            "📝 Examples:\n"
            "• \"Schedule a meeting for Monday 10am with Alice\"\n"
            "• \"The payment API is down! Alert the team!\"\n"
            "• \"Create a ticket for Dana to fix the login bug\"\n"
            "• \"Remind me about the design review tomorrow\"\n\n"
            "💡 Tip: Try compound commands:\n"
            "\"Book a meeting AND create a ticket AND send a reminder\"\n\n"
            "/help - Show more info\n"
            "/status - Show recent activity"
        )

        await update.message.reply_text(welcome)
        CONVERSATIONS[user_id] = {"status": "ready"}


    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = (
            "⚡ ContextOS Help\n\n"
            "This is a Semantic-RPC Bridge that turns natural language into machine actions.\n\n"
            "🛠️ Available Tools:\n"
            "📅 Schedule meetings\n"
            "🚨 Send alerts\n"
            "🎫 Create tickets\n"
            "⏰ Set reminders\n\n"
            "🎯 How to use:\n"
            "1. Write what you want in natural language\n"
            "2. I'll understand your intent\n"
            "3. I'll execute the right tools\n"
            "4. You'll get confirmation\n\n"
            "📊 To see all data:\n"
            "Check data/calendar.json, data/alerts.json, etc.\n\n"
            "/start - Welcome message\n"
            "/status - Recent activity\n"
            "/help - This message"
        )
        await update.message.reply_text(help_text)


    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command."""
        cals = len(_load_json("calendar.json"))
        alts = len(_load_json("alerts.json"))
        tkts = len(_load_json("tickets.json"))
        rems = len(_load_json("reminders.json"))

        status = (
            f"📊 ContextOS Status\n\n"
            f"📅 Calendar: {cals} events\n"
            f"🚨 Alerts: {alts} active\n"
            f"🎫 Tickets: {tkts} open\n"
            f"⏰ Reminders: {rems} pending\n\n"
            f"🟢 All systems operational!"
        )
        await update.message.reply_text(status)


    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming voice messages (Simulated Phone Call)."""
        user_id = update.effective_user.id
        
        # 1. Download File
        voice_file = await update.message.voice.get_file()
        ogg_path = f"temp_audio/{user_id}.ogg"
        await voice_file.download_to_drive(ogg_path)
        
        await update.message.reply_text("👂 Listening...")
        
        # 2. Transcribe (STT)
        text_command = self.voice_processor.transcribe_audio(ogg_path)
        
        if not text_command:
            await update.message.reply_text("❌ Could not understand audio.")
            return

        if text_command.startswith("ERROR:"):
            await update.message.reply_text(f"❌ Voice Error: {text_command}")
            return

        await update.message.reply_text(f"🗣️ You said: '{text_command}'")
        
        # 3. Process Command (AI Brain)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        response_data = await self.orchestrator.route_message(text_command, context={"user_id": user_id})
        
        # Format Text Response for User to see
        text_response = "\n".join(response_data.get("response_lines", []))
        
        # 4. Synthesize Response (TTS)
        # Extract just the spoken part (remove emoji/logs for cleaner audio)
        spoken_text = text_response.replace("*", "").replace("✅", "").replace("❌", "")
        # Limit length for TTS
        if len(spoken_text) > 500:
            spoken_text = spoken_text[:500] + "..."
            
        mp3_path = await self.voice_processor.text_to_speech(spoken_text, f"response_{user_id}.mp3")
        
        if mp3_path and os.path.exists(mp3_path):
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=mp3_path)
            # Also send text trace for debugging
            await update.message.reply_text(f"🤖 Brain Trace:\n{text_response}")
        else:
            await update.message.reply_text(f"❌ TTS Failed. Response:\n{text_response}")

    async def _safe_reply(self, update: Update, text: str, retries: int = 3):
        """Send a reply with retries to handle unstable networks."""
        for attempt in range(retries):
            try:
                await update.message.reply_text(text)
                return
            except Exception as e:
                print(f"⚠️ Reply attempt {attempt+1}/{retries} failed: {e}")
                await asyncio.sleep(2) # Wait a bit longer before retry
        print(f"❌ Failed to reply after {retries} attempts.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming messages — renders rich step-by-step agent responses."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        message_text = update.message.text.strip()

        if not message_text:
            return

        # Show typing indicator (wrapped in try/except to avoid crashing on network blips)
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        except Exception as e:
            # Just log warning, don't crash
            print(f"⚠️ Warning: Could not send typing action: {e}")

        print(f"\n📱 Telegram [{user_name}]: {message_text}")

        try:
            # Get context
            user_context = CONVERSATIONS.get(user_id, {})
            
            # Route through multi-agent system
            result = await self.orchestrator.route_message(message_text, context=user_context)
            
            total_tasks = result.get("total_tasks", 0)
            response_lines = result.get("response_lines", [])
            
            if response_lines:
                # Build rich response from step-by-step agent traces
                header = "⚡ ContextOS Multi-Agent Response\n"
                body = "\n".join(response_lines)
                
                # Add data confirmation footer for action commands
                footer = ""
                if total_tasks > 0:
                    footer = "\n\n📁 Data saved to JSON proof files"
                
                response = f"{header}\n{body}{footer}"
                
                # Also try to send to Slack if it's a delegation message
                await self._send_to_slack_if_needed(message_text, user_name)
            else:
                response = (
                    "🤔 I understood your message but couldn't identify a clear action.\n\n"
                    "💡 Try commands like:\n"
                    "• \"Tell John to fix the bug\"\n"
                    "• \"Schedule meeting with Alice at 3pm\"\n"
                    "• \"Send alert to Dana\"\n"
                    "• \"What meetings do I have?\"\n"
                    "• \"Find the DevOps expert\"\n"
                    "• \"Critical server is down!\"\n"
                    "• \"Reschedule 3pm to 4pm with John\"\n"
                    "• \"Tell Dana the payment bug is fixed\""
                )
            
            await self._safe_reply(update, response)
            
            # Store context
            CONVERSATIONS[user_id] = {
                "last_message": message_text,
                "last_tasks": total_tasks,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"❌ Error processing message: {str(e)}\n\nTry again with a clearer command."
            await self._safe_reply(update, error_msg)


    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle photo messages (future: image analysis)."""
        await update.message.reply_text(
            "📸 Image received!\n\n"
            "Image analysis coming soon. For now, you can:\n"
            "1. Describe the image in text\n"
            "2. Send it with a caption\n\n"
            "Example: 'screenshot showing error 500 - alert the team'"
        )


    async def _send_to_slack_if_needed(self, message_text: str, user_name: str) -> None:
        """Check if message should be sent to Slack and send it."""
        import re
        
        msg_lower = message_text.lower()
        
        # Pattern: "Tell [person]" or "Contact [person]"
        patterns = [
            r'(?:tell|ask|contact|notify)\s+(\w+)\s+(?:to|about|that)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                person_name = match.group(1)
                
                try:
                    # Use intelligent_send to send to Slack
                    result = intelligent_send(person_name, message_text)
                    
                    if result["status"] == "success":
                        print(f"   📤 Slack message sent to {person_name}")
                        msg_result = result.get("message_result", {})
                        if msg_result.get("status") == "success":
                            print(f"   ✅ Message delivered via {msg_result.get('app')}")
                except Exception as e:
                    print(f"   ⚠️  Could not send to Slack: {e}")
                
                break

    def run(self):
        """Start the bot's polling."""
        self.application.run_polling(
            allowed_updates=["message", "text", "photo", "voice"],
            drop_pending_updates=True,
            timeout=30, # Long polling timeout (seconds)
            close_loop=True # Close loop cleanly on exit
        )


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────
def main() -> None:
    """Start the Telegram bot."""
    # Windows-Specific Fix for httpx.ConnectError (ProactorEventLoop vs SSL)
    import platform
    if platform.system() == 'Windows':
        policy = asyncio.WindowsSelectorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)

    print("\n" + "═" * 60)
    print("⚡ ContextOS — Telegram Semantic-RPC Bridge")
    print("═" * 60)
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"📂 Data Directory: {DATA_DIR}")
    print("═" * 60)
    print("Starting bot...\n")

    # Initialize JSON files
    for filename in ["calendar.json", "alerts.json", "tickets.json", "reminders.json"]:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            _save_json(filename, [])
            print(f"✓ Created {filename}")

    # Create and run the bot
    if not TELEGRAM_BOT_TOKEN:
         print("❌ Error: Token not found")
         return

    # Infinite Retry Loop for Resilience
    while True:
        try:
            print("🚀 Bot is running with OPTIMIZED NETWORK SETTINGS (HTTP/1.1, Keep-Alive=20s)!\n")
            
            # CRITICAL: Create a FRESH event loop for each restart
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            bot = TelegramBot(TELEGRAM_BOT_TOKEN)
            bot.run()
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"\n⚠️  CRITICAL ERROR: {e}")
            print("🔄 Restarting bot in 5 seconds...")
            import time
            time.sleep(5)


if __name__ == "__main__":
    main()
