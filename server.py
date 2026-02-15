"""
ContextOS - Semantic RPC Router
MCP Server for the "2 Fast 2 MCP" Hackathon

Translates natural language (via Archestra) into structured machine actions.
The "Hands" of the system - executes tools and stores results as JSON proof.
"""

import json
import os
import uuid
from datetime import datetime

from fastmcp import FastMCP

# ──────────────────────────────────────────────
# Initialize FastMCP Server
# ──────────────────────────────────────────────
mcp = FastMCP("ContextOS")

# Data directory for JSON storage (visible proof for judges)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ──────────────────────────────────────────────
# Helper: Read/Write JSON storage
# ──────────────────────────────────────────────
def _load_json(filename: str) -> list:
    """Load existing entries from a JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_json(filename: str, data: list) -> None:
    """Save entries to a JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _generate_id(prefix: str) -> str:
    """Generate a short unique ID like EVT-a3b8 or TKT-f1d2."""
    return f"{prefix}-{uuid.uuid4().hex[:4]}"


# ──────────────────────────────────────────────
# Tool 1: Schedule Event / Meeting
# ──────────────────────────────────────────────
@mcp.tool()
def schedule_event(topic: str, time: str, participants: list[str]) -> str:
    """
    Schedules a meeting on the team calendar.
    Use this tool when the user mentions 'meeting', 'sync', 'call',
    'standup', 'post-mortem', or a specific time/date.
    Extract the topic and participants from the message.

    Args:
        topic: The meeting topic or subject
        time: When the meeting should happen (e.g., "Monday 10am", "tomorrow 2pm")
        participants: List of participant names or team names

    Returns:
        A confirmation message with the event ID
    """
    event_id = _generate_id("EVT")
    entry = {
        "id": event_id,
        "topic": topic,
        "time": time,
        "participants": participants,
        "created_at": datetime.now().isoformat(),
        "status": "scheduled"
    }

    # Store in JSON
    # Conflict Check (Simple)
    events = _load_json("calendar.json")
    for e in events:
        if e.get("time") == time and e.get("status") != "cancelled":
            # In a real MCP, we might raise an error or ask for confirmation.
            # For this hackathon demo, we log it and proceed with a warning.
            print(f"⚠️ Conflict detected with event: {e.get('topic')}")

    # Generate Meeting Link
    meeting_link = ""
    lower_topic = topic.lower()
    if "google meet" in lower_topic or "meet" in lower_topic:
        meeting_link = f"https://meet.google.com/{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
    elif "zoom" in lower_topic:
        meeting_link = f"https://zoom.us/j/{uuid.uuid4().int % 10**10}?pwd={uuid.uuid4().hex[:8]}"
    elif "teams" in lower_topic:
        meeting_link = f"https://teams.microsoft.com/l/meetup-join/{uuid.uuid4().hex}"

    entry = {
        "id": event_id,
        "topic": topic,
        "time": time,
        "participants": participants,
        "created_at": datetime.now().isoformat(),
        "status": "scheduled",
        "link": meeting_link
    }
    
    events.append(entry)
    _save_json("calendar.json", events)

    # Console log for demo
    print(f"\n[MCP LOG] 📅 ACTION: Scheduling '{topic}' @ {time}")
    print(f"          Participants: {', '.join(participants)}")
    print(f"          Event ID: {event_id}")

    if meeting_link:
        print(f"          Link: {meeting_link}")
        return f"✅ Meeting '{topic}' scheduled for {time}. Link: {meeting_link}. ID: {event_id}"
    
    return f"✅ Meeting '{topic}' scheduled for {time} with {', '.join(participants)}. Event ID: {event_id}"


# ──────────────────────────────────────────────
# Tool 2: Trigger Alert
# ──────────────────────────────────────────────
@mcp.tool()
def trigger_alert(system: str, issue: str, priority: str) -> str:
    """
    Sends an urgent DevOps alert to the on-call team.
    Use this tool when the user mentions 'error', 'down', 'fail',
    'broken', '500', 'outage', or 'crash'.
    Priority must be 'High', 'Medium', or 'Low'.

    Args:
        system: The system or component affected (e.g., "Payment Gateway", "API Server")
        issue: Description of the problem
        priority: Alert priority - must be 'High', 'Medium', or 'Low'

    Returns:
        An alert confirmation with the alert ID
    """
    alert_id = _generate_id("ALT")
    entry = {
        "id": alert_id,
        "system": system,
        "issue": issue,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }

    # Store in JSON
    alerts = _load_json("alerts.json")
    alerts.append(entry)
    _save_json("alerts.json", alerts)

    # Console log for demo
    print(f"\n[MCP LOG] 🚨 ACTION: Triggering Alert for {system} | Priority: {priority}")
    print(f"          Issue: {issue}")
    print(f"          Alert ID: {alert_id}")

    return f"🚨 Alert sent! The {system} team has been notified. Issue: '{issue}' | Priority: {priority} | Alert ID: {alert_id}"


# ──────────────────────────────────────────────
# Tool 3: Create Ticket
# ──────────────────────────────────────────────
@mcp.tool()
def create_ticket(assignee: str, summary: str, due: str, priority: str) -> str:
    """
    Creates a Jira-style task ticket and assigns it to someone.
    Use this tool when the user assigns work, mentions a task, fix,
    action item, or asks someone to do something with a deadline.

    Args:
        assignee: Who the task is assigned to (person or team name)
        summary: Brief description of the task
        due: Deadline or due date (e.g., "Friday 5pm", "end of day")
        priority: Task priority - 'High', 'Medium', or 'Low'

    Returns:
        A ticket confirmation with ticket ID
    """
    ticket_id = _generate_id("TKT")
    entry = {
        "id": ticket_id,
        "assignee": assignee,
        "summary": summary,
        "due": due,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "status": "open"
    }

    # Store in JSON
    tickets = _load_json("tickets.json")
    tickets.append(entry)
    _save_json("tickets.json", tickets)

    # Console log for demo
    print(f"\n[MCP LOG] 🎫 ACTION: Creating Ticket for {assignee}")
    print(f"          Summary: {summary}")
    print(f"          Due: {due} | Priority: {priority}")
    print(f"          Ticket ID: {ticket_id}")

    return f"🎫 Ticket {ticket_id} created! Assigned to {assignee}: '{summary}' | Due: {due} | Priority: {priority}"


# ──────────────────────────────────────────────
# Tool 4: Create Reminder
# ──────────────────────────────────────────────
@mcp.tool()
def create_reminder(message: str, time: str, target: str) -> str:
    """
    Creates a reminder for a person or team.
    Use this tool when the user says 'remind', 'don't forget',
    'follow up', 'check back', or 'ping me'.

    Args:
        message: What to be reminded about
        time: When to trigger the reminder (e.g., "in 2 hours", "tomorrow morning")
        target: Who should receive the reminder (person or team name)

    Returns:
        A reminder confirmation with reminder ID
    """
    reminder_id = _generate_id("REM")
    entry = {
        "id": reminder_id,
        "message": message,
        "time": time,
        "target": target,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }

    # Store in JSON
    reminders = _load_json("reminders.json")
    reminders.append(entry)
    _save_json("reminders.json", reminders)

    # Console log for demo
    print(f"\n[MCP LOG] ⏰ ACTION: Creating Reminder for {target}")
    print(f"          Message: {message}")
    print(f"          When: {time}")
    print(f"          Reminder ID: {reminder_id}")

    return f"⏰ Reminder set! Will remind {target}: '{message}' at {time}. Reminder ID: {reminder_id}"


# ──────────────────────────────────────────────
# Initialize JSON Files at Startup
# ──────────────────────────────────────────────
def _init_json_files():
    """Initialize empty JSON files if they don't exist."""
    for filename in ["calendar.json", "alerts.json", "tickets.json", "reminders.json"]:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            _save_json(filename, [])
            print(f"✓ Created {filename}")


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    _init_json_files()
    
    print("\n" + "═" * 60)
    print("🚀 ContextOS MCP Server")
    print("═" * 60)
    print("📡 SSE Server: http://0.0.0.0:8000/sse")
    print("🔌 Archestra Connection:")
    print("   • Windows/Mac: http://host.docker.internal:8000/sse")
    print("   • Linux: http://172.17.0.1:8000/sse")
    print("\n💾 Data Files: data/")
    print("   • calendar.json | alerts.json | tickets.json | reminders.json")
    print("═" * 60 + "\n")

    try:
        mcp.run(
            transport="sse",
            host="0.0.0.0",
            port=8000
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
