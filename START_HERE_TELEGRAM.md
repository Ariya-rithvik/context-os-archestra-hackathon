🚀 GET STARTED WITH TELEGRAM BOT - 5 MINUTES
═════════════════════════════════════════════════════════════════

This is your quick reference. Everything else is context. Follow these steps.


STEP 1: GET BOT TOKEN (2 MINUTES)
─────────────────────────────────────────────────────────────────

1. Open Telegram (the app or web.telegram.org)

2. Search for: @BotFather
   (It's Telegram's official bot for creating bots)

3. Click on @BotFather and send: /newbot

4. Answer the questions:
   Telegram: What should your bot be called?
   You: ContextOS
   
   Telegram: Give your bot a username.
   You: contextos_<your_name>_bot
   (MUST end with "_bot", must be unique. Example: contextos_demo_bot)

5. Copy the token you receive:
   It looks like: 123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg

   ⚠️  SAVE THIS TOKEN - You need it in Step 2


STEP 2: SET ENVIRONMENT VARIABLE (1 MINUTE)
─────────────────────────────────────────────────────────────────

Choose your operating system:

WINDOWS - Command Prompt (cmd.exe):
  ┌────────────────────────────────────────────────────────────┐
  │ set TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg │
  └────────────────────────────────────────────────────────────┘
  (Replace with your actual token)

WINDOWS - PowerShell:
  ┌────────────────────────────────────────────────────────────┐
  │ $env:TELEGRAM_BOT_TOKEN = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg" │
  └────────────────────────────────────────────────────────────┘
  (Replace with your actual token)

MAC/LINUX - Terminal (bash/zsh):
  ┌────────────────────────────────────────────────────────────┐
  │ export TELEGRAM_BOT_TOKEN="123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg" │
  └────────────────────────────────────────────────────────────┘
  (Replace with your actual token)

✅ The token is now set for this terminal session.
   (You'll need to reset it if you close the terminal)


STEP 3: INSTALL DEPENDENCIES (1 MINUTE)
─────────────────────────────────────────────────────────────────

In your terminal (same one where you set the token):

  pip install -r requirements.txt

This installs:
  • fastmcp (MCP framework)
  • python-telegram-bot (Telegram API)
  • And all other dependencies

You should see: "Successfully installed..." messages


STEP 4: START THE BOT (30 SECONDS)
─────────────────────────────────────────────────────────────────

Choose ONE:

WINDOWS - Use batch script:
  .\START-TELEGRAM.bat

WINDOWS - Use PowerShell:
  .\START-TELEGRAM.ps1

ANY OS - Direct Python:
  python telegram_bot.py

Expected output:
  ⚡ ContextOS — Telegram Semantic-RPC Bridge
  ╔════════════════════════════════════════════════╗
  ║ Bot is running! Send it a message on Telegram. ║
  ╚════════════════════════════════════════════════╝

If you see errors at this point, check:
  ❌ Error: "TELEGRAM_BOT_TOKEN not found"
     → Did you set the environment variable? Go back to Step 2.
  
  ❌ Error: "module 'python_telegram_bot' not found"
     → Did you run pip install? Go back to Step 3.
  
  ❌ Error about token format
     → Is your token correct from @BotFather? Check Step 1.


STEP 5: TEST THE BOT (1 MINUTE)
─────────────────────────────────────────────────────────────────

1. Open Telegram app (or web.telegram.org)

2. Search for your bot username:
   contextos_<your_name>_bot
   (The one you created in Step 1)

3. Click on it to open the conversation

4. Send the command: /start
   ✅ You should see a welcome message:
      "⚡ Welcome to ContextOS!
       I'm your Semantic-RPC Bridge..."

   If you don't see this, the bot didn't start. Check the terminal.

5. Send a command:
   Schedule a meeting for Monday 10am with Alice

6. Bot responds:
   ⚡ Semantic-RPC Bridge Executed
   📅 Calendar
   Meeting 'schedule a meeting for Monday 10am' scheduled for Monday 10am with Alice
   EVT-a3b8

7. Verify the data was saved:
   Check the file: data/calendar.json
   You should see a new entry with ID "EVT-a3b8"

✅ SUCCESS! Your bot is working!


WHAT TO TRY NEXT
─────────────────────────────────────────────────────────────────

Try sending these to your bot:

📅 Calendar:
  "Schedule a standup for Tuesday 10am with Alice and Bob"
  → Creates calendar entry

🚨 Alert:
  "The payment API is down! Alert the team immediately!"
  → Creates alert (High priority)

🎫 Ticket:
  "Create a ticket for Dana to fix the login bug by Friday"
  → Creates ticket assigned to Dana

⏰ Reminder:
  "Remind me about the design review tomorrow morning"
  → Creates reminder

👑 Multi-action (THE WOW MOMENT):
  "The database is down - alert the team immediately, 
   schedule a war room for 2pm, and create a ticket for John to fix it!"
  → Creates ALL THREE - alert, calendar event, and ticket
     in a single message!

Try /help for more commands:
  /start - Welcome message
  /help - Show help
  /status - Show stats (how many events, alerts, etc)


TROUBLESHOOTING
─────────────────────────────────────────────────────────────────

Problem: Bot doesn't respond

Check 1: Is the bot running?
  Look at your terminal. Does it say "Bot is running"?
  If not, restart with: .\START-TELEGRAM.bat

Check 2: Did you hit /start first?
  Send /start to the bot before other commands

Check 3: Is your username correct?
  Search for: contextos_<your_name>_bot
  (Replace <your_name> with what you put in Step 1)

If still stuck:
  Read: TELEGRAM_SETUP.md (detailed 15-minute guide)
  Or ask: Check console output for error messages

---

Problem: "TELEGRAM_BOT_TOKEN is not set" error

Your token got lost when you:
  • Closed the terminal
  • Opened a new terminal
  • Restarted your computer

Solution: Set it again (Step 2)

Pro tip: Set it once in your system environment:
  Windows: Settings → Environment Variables → New
  Mac/Linux: Add to ~/.bashrc or ~/.zshrc (permanent)

---

Problem: No data appearing in data/calendar.json

Check 1: Did the bot respond with an ID?
  If yes (you saw EVT-a3b8): Check data/ folder exists
  If no (you didn't see ID): Bot ran into error

Check 2: Open data/calendar.json manually
  Should be in: d:\context-bridge\data\calendar.json

Check 3: Look at console output
  Any error messages?

If stuck:
  Read: TELEGRAM_SETUP.md → Troubleshooting section

---

Problem: Want to start fresh

Option 1: Just change the token
  Set a new token for a different bot

Option 2: Verify your setup
  Run: pip install -r requirements.txt (again)
  Run: python telegram_bot.py (direct test)

Option 3: Check all data
  Send: /status
  Bot will show: "3 Calendar events, 2 Alerts, 1 Ticket, 4 Reminders"


SHOWING TO JUDGES (DEMO SCRIPT)
─────────────────────────────────────────────────────────────────

You're done when you can show judges this:

1. Open Telegram app while bot is running

2. Say: "Watch this single message trigger 3 different systems:"

3. Send to bot:
   "The payment gateway is down with critical errors.
    This is urgent! Alert the backend team immediately.
    Schedule a war room for today at 2pm. Create a ticket 
    for Sarah to investigate and fix by end of day."

4. Show:
   ✅ Bot responds in <1 second with 3 IDs:
      - 🚨 Alert sent | ALT-xxxx
      - 📅 Meeting scheduled | EVT-xxxx
      - 🎫 Ticket created | TKT-xxxx

5. Judges are impressed: "One message, three actions!"

6. Show the proof:
   Open data/alerts.json, data/calendar.json, data/tickets.json
   Say: "Every action is immutable, timestamped, auditable."

💡 Talking point:
   "This is the Human-to-Machine protocol. Natural language 
    is the USB. The Semantic Router is the driver. 
    This is the future of AI infrastructure."


═════════════════════════════════════════════════════════════════

YOU'RE READY TO START!

Follow the 5 steps above. Should take 5 minutes total.

If you get stuck: Read TELEGRAM_SETUP.md (15-minute guide)

Questions? Check: README.md, ARCHITECTURE_GUIDE.md

Now go! ⚡
