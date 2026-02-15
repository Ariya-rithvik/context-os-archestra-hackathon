⚡ CONTEXTOS - QUICK START GUIDE
═════════════════════════════════════════════════════════════════

The Semantic-RPC Bridge with Telegram as Input Layer


🎯 FASTEST SETUP - TELEGRAM BOT (5 minutes)
─────────────────────────────────────────────────────────────────

Step 1: Get Telegram Bot Token (2 min)
  • Go to: https://t.me/botfather
  • Type: /newbot
  • Name it: ContextOS
  • Copy the token (looks like: 123456:ABCDEFGhijklmnop-xyz)

Step 2: Set Environment Variable (1 min)

  Windows Command:
    set TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
  
  Windows PowerShell:
    $env:TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"
  
  Mac/Linux:
    export TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"

Step 3: Start The Bot (1 min)

  Windows: .\START-TELEGRAM.bat
  Mac/Linux: python telegram_bot.py

Step 4: Test (1 min)

  1. Open Telegram app
  2. Search: @contextos_<your_bot>
  3. Send: /start
  4. Send: "Schedule a meeting for Monday 10am with Alice"
  
  Response: ✅ Meeting scheduled! | EVT-xxxx
  
✅ Done! Your bot is working!

For detailed setup: See TELEGRAM_SETUP.md


💡 WITH DOCKER ARCHESTRA (Full Demo - 5 minutes)
─────────────────────────────────────────────────────────────────

INSTALL:
  docker pull archestra/platform:latest

TERMINAL 1 - Start MCP Server:
  python server.py
  (Output: "📡 SSE Server: http://0.0.0.0:8000/sse")

TERMINAL 2 - Start Archestra:
  docker run -p 3000:3000 -p 9000:9000 \
    -e ARCHESTRA_QUICKSTART=true \
    archestra/platform:latest

BROWSER 1 - Archestra UI:
  http://localhost:3000

BROWSER 2 - (Optional) Dashboard:
  http://localhost:5050

CONFIGURE ARCHESTRA:
  1. Settings → LLM Configuration
     → Add Cerebras API key (free: cerebras.ai)
  
  2. MCP Servers → Add New
     → Type: Remote (SSE)
     → URL: Windows/Mac: http://host.docker.internal:8000/sse
     → URL: Linux: http://172.17.0.1:8000/sse
  
  3. Agents → New Agent
     → Name: "ContextOS"
     → Select all 4 MCP tools
     → System prompt: (see README.md)

CHAT:
  Type: "Schedule a meeting for Monday with the team"
  Watch: Agents assemble in real-time!
  Check: data/calendar.json (entry was created!)


🧪 TEST THE SYSTEM (Copy-paste examples)
─────────────────────────────────────────────────────────────────

Test 1 - Calendar:
  "Can you please schedule a weekly standup for Monday at 10am 
   with Alice, Bob, and the dev team?"
  
  ✓ Expect: calendar.json updated with event ID

Test 2 - Alert:
  "URGENT! The payment gateway is throwing 500 errors! 
   Alert the backend team immediately!"
  
  ✓ Expect: alerts.json updated with HIGH priority

Test 3 - Ticket:
  "Create a task for Dana to fix the login bug by Friday, 
   this is high priority"
  
  ✓ Expect: tickets.json updated with ticket ID

Test 4 - Reminder:
  "Remind the product team about the design review 
   tomorrow morning at 9am"
  
  ✓ Expect: reminders.json updated with reminder ID

Test 5 - Multi-Action:
  "Book a follow-up meeting for tomorrow at 3pm with the team 
   AND create a ticket for Sarah to fix the auth issue by end of day, 
   also remind me to send the notes tonight"
  
  ✓ Expect: All 3 files updated (calendar, tickets, reminders)


🔧 TROUBLESHOOTING
─────────────────────────────────────────────────────────────────

Q: "FastMCP not found"
A: pip install fastmcp>=2.0.0

Q: "Port 8000 already in use"
A: taskkill /F /IM python.exe (Windows)
   killall python (Mac/Linux)

Q: "No data in JSON files"
A: Check the console logs - tool execution messages should appear
   Example: "[MCP LOG] 📅 ACTION: Scheduling 'meeting'..."

Q: "Archestra can't connect to MCP Server"
A: Use correct URL:
   Windows/Mac: http://host.docker.internal:8000/sse
   Linux: http://172.17.0.1:8000/sse

Q: "Data appears in dashboard but not in Archestra"
A: These are separate systems. Dashboard tests the semantic router.
   Archestra uses its own LLM for intent parsing. Both will create
   entries in the JSON files.


📊 WHAT'S HAPPENING BEHIND THE SCENES
─────────────────────────────────────────────────────────────────

Your message:
  "Schedule a meeting for Monday with Alice"
                          ↓
Dashboard OR Archestra receives it
                          ↓
Semantic Router (4-stage pipeline):
  Stage 1: Extract actions from keywords
  Stage 2: Classify as COMMAND vs QUESTION
  Stage 3: Resolve context (times, people, priority)
  Stage 4: Plan RPC calls → schedule_event()
                          ↓
MCP Tools execute:
  schedule_event(topic="meeting", time="Monday", participants=["Alice"])
                          ↓
Result saved to JSON:
  data/calendar.json ← new entry with ID EVT-xxxx
                          ↓
Response returned:
  "✅ Meeting scheduled for Monday. Event ID: EVT-xxxx"


📁 FILES TO CHECK
─────────────────────────────────────────────────────────────────

After running commands, verify:
  data/calendar.json → for scheduled meetings
  data/alerts.json → for triggered alerts
  data/tickets.json → for assigned tasks
  data/reminders.json → for follow-ups

Each file will have entries like:
  {
    "id": "EVT-a3b8",
    "topic": "All-hands standup",
    "time": "Monday 10am",
    "participants": ["Alice", "Bob"],
    "created_at": "2026-02-14T10:30:45.123456",
    "status": "scheduled"
  }


💰 FREE LLM OPTIONS FOR ARCHESTRA
─────────────────────────────────────────────────────────────────

Cerebras (Recommended):
  • Free: 1M tokens/day
  • Setup: Go to cerebras.ai → Create account → Copy API key
  • No credit card needed

Google Gemini:
  • Free: Through AI Studio
  • Setup: ai.google.dev → Get API key

Ollama (Runs Locally):
  • Free: Unlimited, runs on your machine
  • Setup: ollama.com → Download → Run: ollama run mistral


✅ SUCCESS CRITERIA
─────────────────────────────────────────────────────────────────

You're done when:
  ✓ MCP Server starts without errors
  ✓ Dashboard loads at http://localhost:5050 (optional)
  ✓ You can type commands and see agent responses
  ✓ data/calendar.json has new entries
  ✓ data/alerts.json has new entries
  ✓ data/tickets.json has new entries
  ✓ data/reminders.json has new entries


🚀 YOU'RE READY!
─────────────────────────────────────────────────────────────────

Your ContextOS installation is complete and tested.
All components are working.

Next step: Run the demo with Archestra!

Questions? Check README.md for detailed documentation.

═════════════════════════════════════════════════════════════════
