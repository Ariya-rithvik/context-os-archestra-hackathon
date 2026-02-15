"""
⚡ FASTEST POSSIBLE START - 3 COMMANDS
Just run these, that's it!
"""

print("""

╔════════════════════════════════════════════════════════════════════════════╗
║  ⚡ SUPER QUICK START - Just 3 Commands! (Total: 10 minutes)             ║
╚════════════════════════════════════════════════════════════════════════════╝


COMMAND 1: Get Slack Webhook URL (5 minutes)
════════════════════════════════════════════════════════════════════════════

python GET_WEBHOOK_URL.py

👆 Run this command RIGHT NOW!
   It will show you exactly what to click in Slack's website
   You'll get a webhook URL (looks like: https://hooks.slack.com/...)
   Save it somewhere!


COMMAND 2: Run the Demo (Copy & Paste)
════════════════════════════════════════════════════════════════════════════

After you have the webhook URL, paste this in PowerShell:

$env:SLACK_WEBHOOK_URL = "PASTE_YOUR_WEBHOOK_URL_HERE"
cd d:\\context-bridge
python slack_demo_video_ready.py

👆 This shows 3 complete scenarios with agents coordinating


COMMAND 3: Watch in Slack (While Command 2 is running)
════════════════════════════════════════════════════════════════════════════

Open in browser:
https://contextbridge-demo.slack.com

Watch these 4 channels:
  1. #general (agent messages)
  2. #status-board (live updates)
  3. @john (his private messages)
  4. @alice (if meeting scenario)

👆 See agents sending messages in real-time!


════════════════════════════════════════════════════════════════════════════

THAT'S IT! YOU'LL SEE:

✅ Terminal showing agent activity
✅ Slack #general getting messages
✅ Slack @john getting private notifications
✅ Slack #status-board showing live progress
✅ Complete coordination in 2-3 seconds

════════════════════════════════════════════════════════════════════════════


OPTIONAL - See What Gets Logged
════════════════════════════════════════════════════════════════════════════

After demo runs:

type data\\slack_agent_logs.json

👆 Shows complete audit trail (every agent action timestamped)


════════════════════════════════════════════════════════════════════════════

WANT TO UNDERSTAND MORE?
════════════════════════════════════════════════════════════════════════════

python QUICK_REFERENCE.py       (all commands on one screen)
python VISUAL_WORKFLOW.py       (shows what happens at each step)
python RUN_DEMO_NOW.py          (interactive step-by-step)

════════════════════════════════════════════════════════════════════════════

READY? Run Command 1 NOW! 👉

python GET_WEBHOOK_URL.py

════════════════════════════════════════════════════════════════════════════
""")
