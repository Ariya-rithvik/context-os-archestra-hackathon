#!/usr/bin/env python3
"""
🚀 SETUP CHECKLIST & RUN GUIDE
For running ContextBridge on Telegram + Slack
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     CONTEXTBRIDGE SETUP CHECKLIST                          ║
║                  Before Running: Complete These Steps                       ║
╚════════════════════════════════════════════════════════════════════════════╝

""")

# ============================================================================
# PART 1: TELEGRAM SETUP
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: TELEGRAM SETUP (5 minutes)                                         │
└─────────────────────────────────────────────────────────────────────────────┘

✅ WHAT YOU NEED:
   • Telegram mobile app or telegram.org (desktop)
   • A Telegram bot token (unique to your bot)
   • The bot username

═══════════════════════════════════════════════════════════════════════════════

📱 Option A: USE EXISTING BOT (Already Set Up)

   Bot Token:  YOUR_TELEGRAM_BOT_TOKEN
   Bot Name:   @ContextOS_Bot
   
   ✅ Just verify the bot works:
      1. Open Telegram
      2. Search for: @ContextOS_Bot
      3. Click START
      4. Should show: "Hi! I'm your intelligent assistant"
      
   ✅ If it doesn't exist, bot is offline (we'll start it in next steps)

═══════════════════════════════════════════════════════════════════════════════

🤖 Option B: CREATE YOUR OWN BOT (If you want to test with your own)

   STEPS:
   1. Open Telegram
   2. Search for: @BotFather
   3. Send: /start
   4. Send: /newbot
   5. Choose a name: "MyContextBot" 
   6. Choose username: "MyContextBot_username"
   7. Copy the token: 123456789:ABCdefGHijKLmnoPQRstuvWxyz
   
   SAVE THIS TOKEN - You'll need it! ↓
   Replace in: TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"

═══════════════════════════════════════════════════════════════════════════════

✨ WHAT HAPPENS WHEN BOT STARTS:
   • Bot appears online in Telegram
   • You can message it
   • Bot responds with processed messages
   • All agents start working

""")

# ============================================================================
# PART 2: SLACK SETUP
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: SLACK SETUP (10 minutes)                                           │
└─────────────────────────────────────────────────────────────────────────────┘

✅ WHAT YOU NEED:
   • Slack workspace (create free at slack.com)
   • A Slack channel (#social, #general, etc)
   • A Slack webhook URL

═══════════════════════════════════════════════════════════════════════════════

📝 SETUP INSTRUCTIONS:

1️⃣ CREATE SLACK WORKSPACE (if you don't have one)
   → Go to: slack.com
   → Click: Create new workspace
   → Enter workspace name: "MyTeam"
   → Skip to workspace
   
2️⃣ CREATE SLACK CHANNEL
   → Go to: #channel-browser (bottom left)
   → Click: Create new channel
   → Name: #social (or any name you want)
   → Click Create

3️⃣ GET WEBHOOK URL (This is critical!)
   → Go to: https://api.slack.com/apps
   → Click: Create a new app
   → Choose: From scratch
   → Name: "ContextBridge"
   → Workspace: Select your workspace
   → Click: Create App
   
   → Left sidebar: Incoming Webhooks
   → Toggle: Activate Incoming Webhooks (ON)
   → Click: Add New Webhook to Workspace
   → Select channel: #social
   → Click: Allow
   → COPY the webhook URL: https://hooks.slack.com/services/T123/B456/xyz
   
   SAVE THIS URL - You'll need it! ↓
   Replace in: SLACK_WEBHOOK_URL = "YOUR_WEBHOOK_HERE"

═══════════════════════════════════════════════════════════════════════════════

✨ WHAT HAPPENS WHEN BOT RUNS:
   • Messages appear in #social channel
   • Agent shows who message is for (@john, @rithvik, etc)
   • Timestamp shows when it was sent
   • All automatic - no manual action needed!

""")

# ============================================================================
# PART 3: PYTHON SETUP
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: PYTHON SETUP (2 minutes)                                           │
└─────────────────────────────────────────────────────────────────────────────┘

✅ CHECK PYTHON VERSION:

   Open PowerShell, type:
   python --version
   
   Should show: Python 3.10+ (3.11, 3.12, 3.14 all work)

✅ INSTALL REQUIRED PACKAGES:

   python -m pip install python-telegram-bot
   python -m pip install requests
   python -m pip install aiohttp

   (These might already be installed if you ran before)

═══════════════════════════════════════════════════════════════════════════════

✨ CHECK INSTALLATION:

   python -c "import telegram; print('✅ Telegram library OK')"
   python -c "import requests; print('✅ Requests library OK')"

""")

# ============================================================================
# PART 4: ENVIRONMENT VARIABLES
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: SET ENVIRONMENT VARIABLES                                          │
└─────────────────────────────────────────────────────────────────────────────┘

⚙️  TELEGRAM BOT TOKEN:
   $env:TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
   
   (Or replace with YOUR token if using custom bot)

⚙️  SLACK WEBHOOK URL:
   $env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR_WORKSPACE_ID/YOUR_CHANNEL_ID/YOUR_KEY"
   
   (Or replace with YOUR webhook URL)

═══════════════════════════════════════════════════════════════════════════════

✨ VERIFY VARIABLES ARE SET:

   PowerShell, type:
   echo $env:TELEGRAM_BOT_TOKEN
   echo $env:SLACK_WEBHOOK_URL
   
   Both should show ✅ (not empty)

""")

# ============================================================================
# PART 5: RUN THE BOT
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: START THE BOT                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

🚀 IN POWERSHELL, RUN THIS COMMAND:

   $env:TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"; $env:SLACK_WEBHOOK_URL = "your_webhook_url_here"; python telegram_bot.py

✅ EXPECTED OUTPUT:

   ========================================
   ✅ Telegram Bot Starting...
   ========================================
   
   Setting up webhook configuration...
   ✅ Bot started successfully!
   
   🤖 Telegram bot listening for messages...
   Waiting for messages on @ContextOS_Bot...
   
   Press Ctrl+C to stop

═══════════════════════════════════════════════════════════════════════════════

❌ IF YOU SEE ERRORS:

   Error: "Conflict: terminated by other getUpdates request"
   → Solution: Wait 30 seconds and try again (old connection timeout)
   
   Error: "No module named 'telegram'"
   → Solution: pip install python-telegram-bot
   
   Error: "TELEGRAM_BOT_TOKEN not found"
   → Solution: Set env var first: $env:TELEGRAM_BOT_TOKEN = "..."

""")

# ============================================================================
# PART 6: TEST THE BOT
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: TEST THE SYSTEM (Real-Time)                                        │
└─────────────────────────────────────────────────────────────────────────────┘

🎯 NOW TEST WITH REAL MESSAGES:

SETUP:
   1. Open Telegram (phone or desktop)
   2. Open Slack (#social channel)
   3. Keep PowerShell terminal visible
   4. Arrange windows side-by-side

═══════════════════════════════════════════════════════════════════════════════

TEST 1️⃣: SCHEDULE A MEETING

   SEND in Telegram to @ContextOS_Bot:
   "Schedule meeting Monday 10am with Alice"
   
   WATCH:
   📍 Terminal: Shows "CalendarAgent: 📅 Scheduled..."
   📍 Slack: No message (just scheduling, no delegatio n)
   📍 File: data/calendar.json updated with new event
   
   ✅ RESULT: Calendar event created

═══════════════════════════════════════════════════════════════════════════════

TEST 2️⃣: SEND ALERT

   SEND in Telegram:
   "Server crashed!"
   
   WATCH:
   📍 Terminal: Shows "AlertAgent: 🚨 Alert sent..."
   📍 Slack: No message (no delegation)
   📍 File: data/alerts.json updated
   
   ✅ RESULT: Alert created

═══════════════════════════════════════════════════════════════════════════════

TEST 3️⃣: DELEGATION (THE KEY TEST!)

   SEND in Telegram:
   "Tell John to fix the critical bug ASAP"
   
   WATCH CLOSELY:
   
   📍 Terminal shows:
      ⚡ Processing: Tell John to fix the critical bug ASAP
         ✅ AlertAgent: 🚨 Alert sent (priority: High)
         ✅ TaskAgent: 🎫 Ticket created...
         
         🧠 Agent Chain of Thought:
         ✅ Found contact: John
         ✅ Checking activity: 🟢 ACTIVE on Slack (2 mins ago)
         ✅ Decision: Send via SLACK
         ✅ Sending message...
         
         📤 Result:
         Status: success
   
   📍 Slack #social channel shows:
      💬 [Message from Agent]
         Tell John to fix the critical bug ASAP
         To: @john
         Sent: 22:15:17
      
   ✅ RESULT: Message appeared AUTOMATICALLY in Slack!

═══════════════════════════════════════════════════════════════════════════════

TEST 4️⃣: MULTIPLE PEOPLE

   SEND in Telegram:
   "Server is down! Tell Dana to investigate"
   
   WATCH:
   📍 Terminal: Shows agents working
   📍 Slack: Another message appears automatically for @dana!
   
   ✅ RESULT: Different person, intelligent routing!

═══════════════════════════════════════════════════════════════════════════════

✨ YOU'RE NOW SEEING:

   ✅ Telegram → Agent Processing → Slack Delivery (5 seconds!)
   ✅ Messages sent automatically (no manual routing)
   ✅ Agent reasoning visible (chain-of-thought)
   ✅ Different people get messages (intelligent routing)
   ✅ Full audit trail in JSON files

""")

# ============================================================================
# PART 7: VIEW THE DATA
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: VIEW THE AUDIT TRAIL                                               │
└─────────────────────────────────────────────────────────────────────────────┘

After running tests, check what was created:

📅 SEE SCHEDULED MEETINGS:
   Get-Content data/calendar.json | ConvertFrom-Json | Select-Object -Last 3 | Format-Table

🚨 SEE ALERTS CREATED:
   Get-Content data/alerts.json | ConvertFrom-Json | Select-Object -Last 3 | Format-Table

🎫 SEE TICKETS ASSIGNED:
   Get-Content data/tickets.json | ConvertFrom-Json | Select-Object -Last 3 | Format-Table

💬 SEE MESSAGES SENT:
   Get-Content data/messages.json | ConvertFrom-Json | Select-Object -Last 3 | Format-Table

✅ EVERYTHING IS LOGGED AND IMMUTABLE!

""")

# ============================================================================
# PART 8: RUN DEMOS
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: BUILT-IN DEMOS (To Show Others)                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Instead of typing messages, run pre-made demos:

🎬 DEMO 1: ALL AGENTS AT ONCE
   python quick_demo.py
   
   Shows: Calendar, Alerts, Tasks, Smart Messages
   Time: ~1 minute
   Great for: Showing all 4 agent types

═══════════════════════════════════════════════════════════════════════════════

🎬 DEMO 2: SMART MESSAGE GENERATION
   python demo_messaging.py
   
   Shows: Context-aware message generation
   Time: ~30 seconds
   Great for: Showing intelligent message crafting

═══════════════════════════════════════════════════════════════════════════════

🎬 DEMO 3: FULL TELEGRAM → SLACK FLOW
   $env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR_WORKSPACE_ID/YOUR_CHANNEL_ID/YOUR_KEY"; python demo_telegram_to_slack.py
   
   Shows: End-to-end flow with Slack integration
   Time: ~1 minute
   Great for: Showing complete architecture

""")

# ============================================================================
# PART 9: TROUBLESHOOTING
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 9: TROUBLESHOOTING                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

❌ TELEGRAM BOT NOT RESPONDING

   Problem: Bot starts but doesn't respond to messages
   Solution:
      1. Make sure you're messaging the correct bot
      2. Click START in Telegram first
      3. Wait 5 seconds after bot starts
      4. Try again
   
   Check: Type "hello" in Telegram, should get response

═══════════════════════════════════════════════════════════════════════════════

❌ SLACK MESSAGE NOT APPEARING

   Problem: Slide shows status "success" but message not in Slack
   Solution:
      1. Check: Is Slack logged in?
      2. Check: Is #social channel open and visible?
      3. Check: Is webhook URL correct?
      4. Workaround: Try refreshing Slack (F5)
   
   Test webhook directly:
   $env:SLACK_WEBHOOK_URL = "..."; python slack_integration.py

═══════════════════════════════════════════════════════════════════════════════

❌ "CONFLICT: TERMINATED BY OTHER GETUPDATES REQUEST"

   Problem: Bot won't start, says another connection is active
   Solution:
      1. Wait 30-60 seconds (Telegram releases connection)
      2. Try starting bot again
      3. If still fails: Restart your machine
   
   This is a Telegram API issue, not your code

═══════════════════════════════════════════════════════════════════════════════

❌ "MODULE NOT FOUND: TELEGRAM"

   Problem: ImportError: No module named 'telegram'
   Solution:
      pip install python-telegram-bot
      pip install requests
      pip install aiohttp

═══════════════════════════════════════════════════════════════════════════════

✅ TO DEBUG:

   1. Check environment variables:
      echo $env:TELEGRAM_BOT_TOKEN
      echo $env:SLACK_WEBHOOK_URL
   
   2. Test Slack webhook directly:
      python slack_integration.py
   
   3. Check JSON files are updating:
      Get-Content data/calendar.json
   
   4. Read terminal output carefully (shows what's happening)

""")

# ============================================================================
# PART 10: SUMMARY
# ============================================================================

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUICK REFERENCE: 5-MINUTE STARTUP                                          │
└─────────────────────────────────────────────────────────────────────────────┘

⚡ FASTEST WAY TO GET RUNNING:

1. Open PowerShell, go to: cd d:\\context-bridge

2. Copy-paste this command (all one line):
   $env:TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"; $env:SLACK_WEBHOOK_URL = "your_webhook_url_here"; python telegram_bot.py

3. Open Telegram, search: @ContextOS_Bot

4. Open Slack, go to: #social channel

5. Send message in Telegram: "Tell John to fix the bug"

6. Watch Slack - message appears! 🎉

═══════════════════════════════════════════════════════════════════════════════

✅ CHECKLIST BEFORE RUNNING:

   ☐ Python installed (python --version)
   ☐ Libraries installed (pip install python-telegram-bot requests)
   ☐ Telegram app open
   ☐ Slack workspace open (#social channel created)
   ☐ Webhook URL copied from https://api.slack.com/apps
   ☐ Environment variables set (TELEGRAM_BOT_TOKEN, SLACK_WEBHOOK_URL)
   ☐ PowerShell terminal ready in d:\\context-bridge

═══════════════════════════════════════════════════════════════════════════════

🎯 SUCCESS INDICATORS:

   ✅ Terminal shows: "Telegram bot listening for messages..."
   ✅ You message @ContextOS_Bot in Telegram
   ✅ Agent processes (shows in terminal)
   ✅ Message appears in Slack #social automatically
   ✅ data/messages.json gets updated
   ✅ You see chain-of-thought reasoning

═══════════════════════════════════════════════════════════════════════════════

📞 NEED HELP?

   Check: PRODUCTION_GUIDE.md (comprehensive guide)
   Check: ARCHITECTURE_GUIDE.md (technical details)
   Check: Terminal output (shows what's happening)

═══════════════════════════════════════════════════════════════════════════════

🎉 YOU'RE READY TO RUN!

   Your system is production-ready and verified working!
   
   Next: Send test messages and watch it work! 🚀

""")

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    GOOD LUCK! YOU'VE GOT THIS! 🚀                         ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
