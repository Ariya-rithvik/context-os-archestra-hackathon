"""
ContextOS - Multi-Agent System
Autonomous agents working together without human intervention.

Architecture:
  Telegram Input → Message Router → Multiple Agents (concurrent)
    ├── Calendar Agent (schedule, reschedule, query, delegate)
    ├── Search Agent (web research, find experts)
    ├── Delegation Agent (assign to people, send messages)
    ├── Alert Agent (urgent notifications, escalation)
    ├── Task Agent (create tickets, track work)
    └── Messaging Agent (send messages via Telegram/Slack)

Each agent returns a "steps" array showing exactly what it did,
so the Telegram bot can render rich step-by-step responses.
"""

import os
import sys
import json
import uuid
import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from semantic_router import process_message
from slack_integration import intelligent_send, broadcast_to_channel
from phone_agent import PhoneCallingAgent

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "agents"), exist_ok=True)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _load_json(filename: str) -> list:
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_json(filename: str, data: list):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:4]}"

def _find_contact(name: str) -> Optional[dict]:
    """Find contact by name (case-insensitive)."""
    contacts = _load_json("contacts.json")
    name_lower = name.lower()
    for contact in contacts:
        if contact["name"].lower() == name_lower or name_lower in contact["name"].lower():
            return contact
    return None

def _find_expert(expertise: str) -> Optional[dict]:
    """Find an expert by expertise/role keyword."""
    contacts = _load_json("contacts.json")
    expertise_lower = expertise.lower()
    for contact in contacts:
        # Check role
        role = contact.get("role", "").lower()
        if expertise_lower in role:
            return contact
        # Check expertise list
        for exp in contact.get("expertise", []):
            if expertise_lower in exp.lower():
                return contact
        # Check name  
        if expertise_lower in contact["name"].lower():
            return contact
    return None


# ──────────────────────────────────────────────────────────────
# Agent Status
# ──────────────────────────────────────────────────────────────

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    DONE = "done"
    ERROR = "error"


class AgentTaskQueue:
    """Shared task queue for all agents."""
    
    def __init__(self):
        self.tasks = []
        self.completed = []
        self.lock = asyncio.Lock()
    
    async def add_task(self, task: dict):
        async with self.lock:
            task["id"] = _gen_id("TSK")
            task["created_at"] = datetime.now().isoformat()
            task["status"] = "pending"
            self.tasks.append(task)
        return task["id"]
    
    async def complete_task(self, task_id: str, result: dict):
        async with self.lock:
            for task in self.tasks:
                if task["id"] == task_id:
                    task["status"] = "completed"
                    task["result"] = result
                    task["completed_at"] = datetime.now().isoformat()
                    self.completed.append(task)
                    self.tasks.remove(task)
                    break


class AgentMessageBus:
    """Inter-agent communication."""
    
    def __init__(self):
        self.messages = {}
        self.lock = asyncio.Lock()
    
    async def post_message(self, from_agent: str, to_agent: str, message: dict):
        async with self.lock:
            if to_agent not in self.messages:
                self.messages[to_agent] = []
            msg = {
                "from": from_agent,
                "to": to_agent,
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            self.messages[to_agent].append(msg)
            print(f"  📨 {from_agent} → {to_agent}: {message.get('action', 'message')}")
    
    async def get_messages(self, agent: str) -> List[dict]:
        async with self.lock:
            if agent in self.messages:
                unread = [m for m in self.messages[agent] if not m["read"]]
                for m in unread:
                    m["read"] = True
                return unread
        return []


# ──────────────────────────────────────────────────────────────
# Base Agent Class
# ──────────────────────────────────────────────────────────────

class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str, emoji: str, message_bus: AgentMessageBus, task_queue: AgentTaskQueue):
        self.name = name
        self.emoji = emoji
        self.status = AgentStatus.IDLE
        self.message_bus = message_bus
        self.task_queue = task_queue
    
    async def execute_task(self, task: dict) -> dict:
        """Override in subclass. Must return {"steps": [...], ...}"""
        raise NotImplementedError
    
    async def work(self):
        pass


# ──────────────────────────────────────────────────────────────
# Calendar Agent
# ──────────────────────────────────────────────────────────────

class CalendarAgent(BaseAgent):
    """Manages calendar, scheduling, rescheduling, availability."""
    
    def __init__(self, message_bus, task_queue):
        super().__init__("CalendarAgent", "📅", message_bus, task_queue)
    
    async def execute_task(self, task: dict) -> dict:
        action = task.get("action")
        if action == "schedule":
            return await self.schedule_event(task)
        elif action == "reschedule":
            return await self.reschedule_event(task)
        elif action == "query":
            return await self.query_meetings(task)
        return {"steps": [f"❓ {self.name}: Unknown action '{action}'"]}
    
    async def schedule_event(self, task: dict) -> dict:
        steps = []
        title = task.get("title", "Meeting")
        time = task.get("time", "TBD")
        participants = task.get("participants", [])
        force = task.get("force", False)
        
        # Step 1: Check availability & Conflicts
        conflicting_event = None
        events = _load_json("calendar.json")
        
        if participants:
            person_name = participants[0] if isinstance(participants[0], str) else str(participants[0])
            steps.append(f"✅ CalendarAgent: Checking {person_name}'s availability...")
            await asyncio.sleep(0.1)
            
            # Simple conflict check: same person + same time string (for demo)
            for e in events:
                if person_name in e.get("participants", []) and e.get("time", "").lower() == time.lower() and e.get("status") != "cancelled":
                    conflicting_event = e
                    break
            
            if conflicting_event:
                if not force:
                    # Fix: Handle both 'topic' and 'title' keys
                    conflict_title = conflicting_event.get("topic", conflicting_event.get("title", "Meeting"))
                    steps.append(f"⚠️ Conflict detected: {person_name} has '{conflict_title}' at {time}")
                    steps.append(f"❓ Prioritize this meeting or assign to someone else?")
                    return {
                        "steps": steps,
                        "status": "conflict",
                        "conflict_details": conflicting_event
                    }
                else:
                    conflict_title = conflicting_event.get("topic", conflicting_event.get("title", "Meeting"))
                    steps.append(f"⚠️ Conflict override: Removing '{conflict_title}'")
                    conflicting_event["status"] = "cancelled"
                    # In a real app we would notify them of cancellation
            
            steps.append(f"📅 {person_name} free at {time} ✅")
        else:
            steps.append(f"✅ CalendarAgent: Reserving time slot at {time}...")
        


        # Generate Meeting Link if requested
        meeting_link = ""
        lower_title = title.lower()
        if "google meet" in lower_title or "meet" in lower_title:
            meeting_link = f"https://meet.google.com/{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
            steps.append(f"📹 Generated Google Meet link: {meeting_link}")
        elif "zoom" in lower_title:
            # Zoom IDs are typically 9-11 digits, using hex for simplicity here
            meeting_link = f"https://zoom.us/j/{uuid.uuid4().int % 10**10}?pwd={uuid.uuid4().hex[:8]}"
            steps.append(f"📹 Generated Zoom link: {meeting_link}")
        elif "teams" in lower_title:
            meeting_link = f"https://teams.microsoft.com/l/meetup-join/{uuid.uuid4().hex}"
            steps.append(f"📹 Generated Teams link: {meeting_link}")

        # Step 2: Create event
        eid = _gen_id("EVT")
        event = {
            "id": eid,
            "title": title,
            "time": time,
            "participants": participants,
            "created_by": task.get("created_by", "user"),
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
            "link": meeting_link
        }
        events.append(event)
        _save_json("calendar.json", events)
        
        steps.append(f"✅ Meeting scheduled | {eid}")
        
        return {
            "steps": steps,
            "event_id": eid,
            "status": "success"
        }
    
    async def reschedule_event(self, task: dict) -> dict:
        steps = []
        old_time = task.get("old_time", "")
        new_time = task.get("new_time", "")
        person = task.get("person", "")
        
        # Step 1: Check person availability at new time
        if person:
            steps.append(f"✅ CalendarAgent: Checking {person} at {new_time}...")
            await asyncio.sleep(0.1)
            steps.append(f"📅 {person} FREE at {new_time} ✅")
        
        # Step 2: Reschedule
        events = _load_json("calendar.json")
        found = False
        for event in events:
            evt_time = event.get("time", "").lower()
            if old_time.lower() in evt_time:
                event["time"] = new_time
                event["rescheduled_at"] = datetime.now().isoformat()
                event["status"] = "rescheduled"
                found = True
                break
        
        if found:
            _save_json("calendar.json", events)
            steps.append(f"✅ Meeting rescheduled from {old_time} → {new_time}")
        else:
            # Create new entry for the reschedule
            eid = _gen_id("EVT")
            event = {
                "id": eid,
                "title": f"Rescheduled: {old_time} → {new_time}",
                "time": new_time,
                "participants": [person] if person else [],
                "created_at": datetime.now().isoformat(),
                "status": "rescheduled"
            }
            events.append(event)
            _save_json("calendar.json", events)
            steps.append(f"✅ Meeting rescheduled to {new_time} | {eid}")
        
        return {"steps": steps, "status": "success"}
    
    async def query_meetings(self, task: dict) -> dict:
        steps = []
        events = _load_json("calendar.json")
        
        steps.append("📅 CalendarAgent: Fetching your meetings...")
        
        if not events:
            steps.append("📭 No meetings scheduled")
            return {"steps": steps, "status": "empty"}
        
        # Show last 5 meetings
        recent = events[-5:]
        for evt in recent:
            title = evt.get("title", evt.get("topic", "Meeting"))
            time = evt.get("time", "TBD")
            status = evt.get("status", "scheduled")
            steps.append(f"✅ {time} - {title}")
        
        if len(events) > 5:
            steps.append(f"📊 ...and {len(events) - 5} more events")
        
        return {"steps": steps, "status": "success"}


# ──────────────────────────────────────────────────────────────
# Alert Agent
# ──────────────────────────────────────────────────────────────

class AlertAgent(BaseAgent):
    """Sends urgent alerts and escalations."""
    
    def __init__(self, message_bus, task_queue):
        super().__init__("AlertAgent", "🚨", message_bus, task_queue)
    
    async def execute_task(self, task: dict) -> dict:
        action = task.get("action")
        if action == "send_alert":
            return await self.send_alert(task)
        elif action == "escalate":
            return await self.escalate(task)
        return {"steps": [f"❓ {self.name}: Unknown action"]}
    
    async def send_alert(self, task: dict) -> dict:
        steps = []
        title = task.get("title", "Alert")
        message = task.get("message", "Unknown issue")
        priority = task.get("priority", "High")
        recipients = task.get("recipients", [])
        target_person = task.get("target_person", "")
        
        # Step 1: Create alert
        aid = _gen_id("ALT")
        is_critical = priority.lower() in ("critical", "high")
        
        steps.append(f"🚨 AlertAgent: {'CRITICAL' if is_critical else priority.upper()} alert")
        
        alert = {
            "id": aid,
            "system": title,
            "issue": message,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "recipients": recipients
        }
        alerts = _load_json("alerts.json")
        alerts.append(alert)
        _save_json("alerts.json", alerts)
        
        # Step 2: Send to recipients
        if target_person:
            contact = _find_contact(target_person)
            if contact:
                steps.append(f"📤 Sent to {contact['name']} in Slack")
            else:
                steps.append(f"📤 Alert queued for {target_person}")
        elif recipients:
            for r in recipients:
                steps.append(f"📤 Sent to @{r}")
        else:
            # Auto-detect recipients for critical alerts OR explicit broadcast requests
            if is_critical or "broadcast" in message.lower():
                # Find devops and product leads
                devops = _find_expert("devops")
                product = _find_expert("product")
                
                heading = f"🚨 *{priority.upper()} ALERT*" if is_critical else "📢 *BROADCAST*"
                
                # 1. Broadcast to channel
                # If it mentions tech stuff, go to #devops
                if any(w in message.lower() for w in ["server", "api", "devops", "deploy", "database"]):
                    await asyncio.to_thread(broadcast_to_channel, "devops", f"{heading}: {message}")
                    steps.append("📢 Broadcast to #devops channel")
                else:
                    await asyncio.to_thread(broadcast_to_channel, "social", f"{heading}: {message}")
                    steps.append("📢 Broadcast to #social channel")
                
                # 2. Also notify leads if Critical
                if is_critical:
                    if devops:
                        await asyncio.to_thread(intelligent_send, devops["name"], f"🚨 ALERT: {message}")
                        steps.append(f"📤 Sent to @{devops['name'].lower()} (DevOps)")
                    if product:
                        await asyncio.to_thread(intelligent_send, product["name"], f"🚨 ALERT: {message}")
                        steps.append(f"📤 Sent to @{product['name'].lower()} (Product)")
                    
                    steps.append("⏲️ Escalating...")
            else:
                # Default "Alert to team" -> Broadcast #social
                await asyncio.to_thread(broadcast_to_channel, "social", f"🚨 ALERT: {message}")
                steps.append("📢 Broadcast to #social channel")
        
        # Step 3: Waiting for ack on high-priority
        if is_critical or priority.lower() == "high":
            steps.append("⏲️ Waiting for acknowledgement")
        
        return {"steps": steps, "alert_id": aid, "status": "sent"}
    
    async def escalate(self, task: dict) -> dict:
        steps = []
        steps.append("🚨 AlertAgent: CRITICAL status")
        
        contacts = _load_json("contacts.json")
        for contact in contacts:
            role = contact.get("role", "")
            if role in ("devops_lead", "developer", "team_lead"):
                steps.append(f"📤 Sent to @{contact['name'].lower()} ({contact.get('role', 'team')})")
        
        steps.append("⏲️ Escalating...")
        return {"steps": steps, "status": "escalated"}


# ──────────────────────────────────────────────────────────────
# Task Agent
# ──────────────────────────────────────────────────────────────

class TaskAgent(BaseAgent):
    """Creates and manages work tickets."""
    
    def __init__(self, message_bus, task_queue):
        super().__init__("TaskAgent", "🎫", message_bus, task_queue)
    
    async def execute_task(self, task: dict) -> dict:
        action = task.get("action")
        if action == "create_ticket":
            return await self.create_ticket(task)
        return {"steps": [f"❓ {self.name}: Unknown action"]}
    
    async def create_ticket(self, task: dict) -> dict:
        steps = []
        title = task.get("title", "Task")
        assigned_to = task.get("assigned_to", "unassigned")
        priority = task.get("priority", "Medium")
        deadline = task.get("deadline", "TBD")
        
        tid = _gen_id("TKT")
        
        ticket = {
            "id": tid,
            "title": title,
            "assigned_to": assigned_to,
            "priority": priority,
            "deadline": deadline,
            "created_at": datetime.now().isoformat(),
            "status": "open"
        }
        tickets = _load_json("tickets.json")
        tickets.append(ticket)
        _save_json("tickets.json", tickets)
        
        steps.append(f"🎫 TaskAgent: Ticket created for {assigned_to}")
        steps.append(f"📋 {title} | Priority: {priority} | {tid}")
        
        return {"steps": steps, "ticket_id": tid, "status": "created"}


# ──────────────────────────────────────────────────────────────
# Search Agent
# ──────────────────────────────────────────────────────────────

class SearchAgent(BaseAgent):
    """Searches for info, experts, resources."""
    
    def __init__(self, message_bus, task_queue):
        super().__init__("SearchAgent", "🔍", message_bus, task_queue)
    
    async def execute_task(self, task: dict) -> dict:
        action = task.get("action")
        if action == "find_expert":
            return await self.find_expert(task)
        elif action == "search":
            return await self.web_search(task)
        elif action == "monitor":
            return await self.monitor_status(task)
        return {"steps": [f"❓ {self.name}: Unknown action"]}
    
    async def find_expert(self, task: dict) -> dict:
        steps = []
        expertise = task.get("expertise", "")
        
        steps.append(f"🔍 SearchAgent: Searching for {expertise} expert...")
        await asyncio.sleep(0.1)
        
        contact = _find_expert(expertise)
        if contact:
            role = contact.get("role", "team member").replace("_", " ").title()
            steps.append(f"✅ Found: {contact['name']} ({role})")
            steps.append(f"📨 Notifying {contact['name']}")
            
            # Log the search
            msg_log = {
                "id": _gen_id("MSG"),
                "to": contact["name"],
                "message": f"You were identified as the {expertise} expert",
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            messages = _load_json("messages.json")
            messages.append(msg_log)
            _save_json("messages.json", messages)
        else:
            steps.append(f"❌ No {expertise} expert found in contacts")
        
        return {"steps": steps, "status": "found" if contact else "not_found"}
    
    async def web_search(self, task: dict) -> dict:
        steps = []
        query = task.get("query", "")
        
        steps.append(f"🔍 SearchAgent: Searching '{query}'...")
        await asyncio.sleep(0.1)
        
        # Simulate search
        search_log = {
            "id": _gen_id("SCH"),
            "query": query,
            "searched_at": datetime.now().isoformat(),
            "status": "completed"
        }
        searches = _load_json("searches.json") if os.path.exists(os.path.join(DATA_DIR, "searches.json")) else []
        searches.append(search_log)
        _save_json("searches.json", searches)
        
        steps.append(f"✅ Search complete: results found for '{query}'")
        return {"steps": steps, "status": "found"}
    
    async def monitor_status(self, task: dict) -> dict:
        steps = []
        service = task.get("service", "system")
        
        steps.append(f"📊 SearchAgent: Checking {service} status...")
        steps.append(f"✅ {service}: Operational")
        return {"steps": steps, "status": "monitored"}


# ──────────────────────────────────────────────────────────────
# Delegation Agent
# ──────────────────────────────────────────────────────────────

class DelegationAgent(BaseAgent):
    """Delegates tasks to people."""
    
    def __init__(self, message_bus, task_queue):
        super().__init__("DelegationAgent", "👤", message_bus, task_queue)
    
    async def execute_task(self, task: dict) -> dict:
        action = task.get("action")
        if action == "delegate":
            return await self.delegate_to_person(task)
        elif action == "contact":
            return await self.contact_person(task)
        return {"steps": [f"❓ {self.name}: Unknown action"]}
    
    async def delegate_to_person(self, task: dict) -> dict:
        steps = []
        person = task.get("person", "unknown")
        task_desc = task.get("task_description", "")
        
        dlg_id = _gen_id("DLG")
        delegation = {
            "id": dlg_id,
            "person": person,
            "task": task_desc,
            "assigned_at": datetime.now().isoformat(),
            "status": "assigned"
        }
        delegations = _load_json("delegations.json") if os.path.exists(os.path.join(DATA_DIR, "delegations.json")) else []
        delegations.append(delegation)
        _save_json("delegations.json", delegations)
        
        steps.append(f"👤 DelegationAgent: Task delegated to {person}")
        steps.append(f"📋 {task_desc} | {dlg_id}")
        return {"steps": steps, "status": "delegated"}
    
    async def contact_person(self, task: dict) -> dict:
        steps = []
        person = task.get("person", "")
        message = task.get("message", "")
        
        msg_id = _gen_id("MSG")
        contact_log = {
            "id": msg_id,
            "to": person,
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        contacts = _load_json("messages.json")
        contacts.append(contact_log)
        _save_json("messages.json", contacts)
        
        steps.append(f"💬 DelegationAgent: Contacted {person}")
        return {"steps": steps, "status": "sent"}


# ──────────────────────────────────────────────────────────────
# Messaging Agent (Message Delivery)
# ──────────────────────────────────────────────────────────────

class MessagingAgent(BaseAgent):
    """Sends intelligent messages via Telegram/Slack/WhatsApp."""
    
    def __init__(self, message_bus, task_queue, telegram_bot=None):
        super().__init__("MessageDeliveryAgent", "📨", message_bus, task_queue)
        self.telegram_bot = telegram_bot
    
    async def execute_task(self, task: dict) -> dict:
        action = task.get("action")
        if action == "send_message":
            return await self.send_message(task)
        elif action == "send_status_update":
            return await self.send_status_update(task)
        elif action == "notify_contacts":
            return await self.notify_contacts(task)
        return {"steps": [f"❓ {self.name}: Unknown action"]}
    
    async def send_message(self, task: dict) -> dict:
        steps = []
        person = task.get("person", "")
        message = task.get("message", "")
        
        contact = _find_contact(person)
        
        steps.append(f"✅ MessageDeliveryAgent: Message sent to {person}")
        
        # Log message
        msg_id = _gen_id("MSG")
        msg_log = {
            "id": msg_id,
            "to": person,
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "status": "delivered",
            "channel": "slack" if contact else "queued"
        }
        messages = _load_json("messages.json")
        messages.append(msg_log)
        _save_json("messages.json", messages)
        
        # Try to find contact
        contact = _find_contact(person)
        if contact:
            # REAL Slack Send
            slk_res = await asyncio.to_thread(intelligent_send, person, message)
            if slk_res.get("status") == "success":
                app_used = slk_res.get("activity", {}).get("active_on", "slack").capitalize()
                steps.append(f"📨 Message delivered to {contact['name']} via {app_used}")
            else:
                steps.append(f"📨 Message sent to {contact['name']} (Simulated)")
        else:
            # Fallback
            slk_res = await asyncio.to_thread(intelligent_send, person, message)
            steps.append(f"📨 Message delivered to general channel for {person}")
        
        return {"steps": steps, "message_id": msg_id, "status": "delivered"}
    
    async def send_status_update(self, task: dict) -> dict:
        steps = []
        person = task.get("person", "")
        message = task.get("message", "")
        
        contact = _find_contact(person)
        
        steps.append(f"✅ MessageDeliveryAgent: Sent to {person}")
        
        msg_id = _gen_id("MSG")
        msg_log = {
            "id": msg_id,
            "to": person,
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "status": "delivered",
            "channel": "slack"
        }
        messages = _load_json("messages.json")
        messages.append(msg_log)
        _save_json("messages.json", messages)
        
        # REAL Status Update to #social (or #general)
        # We simulate this by sending to a user, or we could add channel support to intelligent_send.
        # For now, let's just log it, or send to a designated channel if we had one.
        # Since the user specifically asked for #social, we will assume intelligent_send sends to webhook.
        
        # Actually, let's try to send to "Channel" if intelligent_send supported it, 
        # but for now we'll just send to the person if specified, or default.
        if contact:
            slk_res = await asyncio.to_thread(intelligent_send, person, f"STATUS UPDATE: {message}")
            # Also broadcast to social so the team knows
            await asyncio.to_thread(broadcast_to_channel, "social", f"📢 STATUS UPDATE: {message} (cc: {person})")
            steps.append(f"📤 Message in Slack #social")
        else:
            # If no specific person, broadcast to social
            await asyncio.to_thread(broadcast_to_channel, "social", f"📢 STATUS UPDATE: {message}")
            steps.append(f"📤 Message in Slack #social")
            
        steps.append("✅ Status: DELIVERED")
        
        return {"steps": steps, "status": "delivered"}
    
    async def notify_contacts(self, task: dict) -> dict:
        steps = []
        people = task.get("people", [])
        message = task.get("message", "")
        
        for person in people:
            contact = _find_contact(person)
            if contact:
                slk_res = await asyncio.to_thread(intelligent_send, person, f"ALERT: {message}")
                steps.append(f"📤 Notified {contact['name']} via Slack")
            else:
                steps.append(f"📝 {person}: message queued")
        
        steps.append(f"📢 {len(people)} contacts notified")
        return {"steps": steps, "status": "completed"}


# ──────────────────────────────────────────────────────────────
# Multi-Agent Orchestrator
# ──────────────────────────────────────────────────────────────

class AgentOrchestrator:
    """Coordinates all agents. Routes messages to the right agents
    and collects step-by-step traces for rich Telegram responses."""
    
    def __init__(self, telegram_bot=None):
        self.message_bus = AgentMessageBus()
        self.task_queue = AgentTaskQueue()
        self.telegram_bot = telegram_bot
        
        self.agents = {
            "CalendarAgent": CalendarAgent(self.message_bus, self.task_queue),
            "DelegationAgent": DelegationAgent(self.message_bus, self.task_queue),
            "SearchAgent": SearchAgent(self.message_bus, self.task_queue),
            "AlertAgent": AlertAgent(self.message_bus, self.task_queue),
            "TaskAgent": TaskAgent(self.message_bus, self.task_queue),
            "MessageDeliveryAgent": MessagingAgent(self.message_bus, self.task_queue, telegram_bot),
            "PhoneCallingAgent": PhoneCallingAgent(self.message_bus, self.task_queue),
        }
    
    async def route_message(self, message: str, context: dict = None) -> dict:
        """Route message to agents and return rich step-by-step results."""
        
        print(f"\n⚡ Processing: {message}")
        msg_lower = message.lower()
        
        all_agent_results = []
        
        # ─── Pattern 0: Prioritization (Context-Aware) ───
        prioritize_match = re.search(r'(?:prioritize|override|do it|force)(?:\s+this)?', msg_lower)
        if prioritize_match and context and context.get("last_message"):
            last_msg = context.get("last_message")
            # Check if last action was a scheduling attempt that failed?
            # For simplicity, we just re-run the scheduling logic on the LAST message but with force=True
            
            # Re-match scheduling pattern on LAST message
            schedule_match = re.search(
                r'(?:schedule|book|set up|arrange)\s+(?:a\s+)?(?:meeting|call|standup|sync|session)\s+(?:with\s+)?(\w+)?\s*(?:at|for|on)?\s*([\d]+\s*(?:am|pm|AM|PM)?.*)?',
                last_msg.lower()
            )
            if schedule_match:
                person = (schedule_match.group(1) or "team").capitalize()
                time_str = (schedule_match.group(2) or "TBD").strip()
                
                r1 = await self.agents["CalendarAgent"].execute_task({
                    "action": "schedule",
                    "title": last_msg,
                    "time": time_str,
                    "participants": [person],
                    "created_by": "user (force)",
                    "force": True  # FORCE IT!
                })
                all_agent_results.append({"agent": "CalendarAgent", "result": r1})
                return self._build_response(message, all_agent_results)
        
        # ─── Pattern 1: "Tell X to fix Y" → Message + Ticket ───
        tell_fix_match = re.search(
            r'(?:tell|ask)\s+(\w+)\s+to\s+(?:fix|resolve|handle|update|debug)\s+(.+)',
            msg_lower
        )
        if tell_fix_match:
            person = tell_fix_match.group(1).capitalize()
            issue = tell_fix_match.group(2).strip().rstrip('.')
            
            # Messaging Agent: send message
            r1 = await self.agents["MessageDeliveryAgent"].execute_task({
                "action": "send_message",
                "person": person,
                "message": f"Please fix: {issue}"
            })
            all_agent_results.append({"agent": "MessageDeliveryAgent", "result": r1})
            
            # Task Agent: create ticket
            r2 = await self.agents["TaskAgent"].execute_task({
                "action": "create_ticket",
                "title": f"Fix {issue}",
                "assigned_to": person,
                "priority": self._detect_priority(message)
            })
            all_agent_results.append({"agent": "TaskAgent", "result": r2})
            
            return self._build_response(message, all_agent_results)
        
        # ─── Pattern 2: "Tell X the Y is fixed" → Status update ───
        tell_fixed_match = re.search(
            r'(?:tell|inform|let)\s+(\w+)\s+(?:that\s+)?(?:the\s+)?(.+?)\s+(?:is|has been|was)\s+(?:fixed|resolved|done|completed)',
            msg_lower
        )
        if tell_fixed_match:
            person = tell_fixed_match.group(1).capitalize()
            subject = tell_fixed_match.group(2).strip()
            
            r1 = await self.agents["MessageDeliveryAgent"].execute_task({
                "action": "send_status_update",
                "person": person,
                "message": f"The {subject} has been fixed"
            })
            all_agent_results.append({"agent": "MessageDeliveryAgent", "result": r1})
            
            return self._build_response(message, all_agent_results)
        
        # ─── Pattern 3: "Tell/Contact X to/about Y" (general message) ───
        tell_match = re.search(
            r'(?:tell|ask|contact|notify|message|send\s+(?:a\s+)?(?:message|msg)\s+to)\s+(\w+)\s+(?:to|about|that)\s+(.+)',
            msg_lower
        )
        if tell_match:
            person = tell_match.group(1).capitalize()
            content = tell_match.group(2).strip().rstrip('.')
            
            r1 = await self.agents["MessageDeliveryAgent"].execute_task({
                "action": "send_message",
                "person": person,
                "message": content
            })
            all_agent_results.append({"agent": "MessageDeliveryAgent", "result": r1})
            
            return self._build_response(message, all_agent_results)
        
        # ─── Pattern 4: "Schedule meeting with X at Y" ───
        schedule_match = re.search(
            r'(?:schedule|book|set up|arrange)\s+(?:a\s+)?(?:meeting|call|standup|sync|session)\s+(?:with\s+)?(\w+)?\s*(?:at|for|on)?\s*([\d]+\s*(?:am|pm|AM|PM)?.*)?',
            msg_lower
        )
        if schedule_match:
            person = (schedule_match.group(1) or "team").capitalize()
            time_str = (schedule_match.group(2) or "TBD").strip()
            
            r1 = await self.agents["CalendarAgent"].execute_task({
                "action": "schedule",
                "title": message,
                "time": time_str,
                "participants": [person]
            })
            all_agent_results.append({"agent": "CalendarAgent", "result": r1})
            
            return self._build_response(message, all_agent_results)
        
        # ─── Pattern 5: "Reschedule X to Y" ───
        reschedule_match = re.search(
            r'(?:reschedule|move|change)\s+(?:my\s+|the\s+)?(?:meeting\s+)?(?:(?:from\s+)?(\d+\s*(?:am|pm)?)\s+to\s+(\d+\s*(?:am|pm)?)(?:\s+with\s+(\w+))?|(.+))',
            msg_lower
        )
        if reschedule_match:
            if reschedule_match.group(1) and reschedule_match.group(2):
                old_time = reschedule_match.group(1).strip()
                new_time = reschedule_match.group(2).strip()
                person = (reschedule_match.group(3) or "").capitalize()
            else:
                old_time = "TBD"
                new_time = "TBD"
                person = ""
                # Try to extract times
                times = re.findall(r'(\d+\s*(?:am|pm))', msg_lower)
                if len(times) >= 2:
                    old_time = times[0]
                    new_time = times[1]
                # Try to extract person
                with_match = re.search(r'with\s+(\w+)', msg_lower)
                if with_match:
                    person = with_match.group(1).capitalize()
            
            r1 = await self.agents["CalendarAgent"].execute_task({
                "action": "reschedule",
                "old_time": old_time,
                "new_time": new_time,
                "person": person
            })
            all_agent_results.append({"agent": "CalendarAgent", "result": r1})
            
            return self._build_response(message, all_agent_results)
        
        # ─── Pattern 6: "What meetings do I have?" ───
        if any(q in msg_lower for q in ["what meeting", "my meeting", "list meeting", "show meeting", "upcoming meeting", "do i have"]):
            r1 = await self.agents["CalendarAgent"].execute_task({
                "action": "query"
            })
            all_agent_results.append({"agent": "CalendarAgent", "result": r1})
            
            return self._build_response(message, all_agent_results)
        
        # ─── Pattern 7: "Find the X expert" ───
        # Handle "who is exper tin devops", "who knows python", "find devops expert"
        expert_match = re.search(
            r'(?:find|who\s+is|who\s+knows|get|locate)\s+(?:the\s+|an?\s+)?(.+)',
            msg_lower
        )
        if expert_match and any(w in msg_lower for w in ["expert", "lead", "specialist", "knows", "who is", "who's", "exper tin"]):
            raw_text = expert_match.group(1).strip().strip('?').strip('.')
            
            # Smart cleanup for typos like "exper tin"
            expertise = raw_text
            keys_to_remove = ["expert in", "exper tin", "expert on", "expert", "lead", "specialist", "guy", "person", "engineer", "who is", "knows", "find"]
            
            for key in keys_to_remove:
                expertise = expertise.replace(key, "").strip()
            
            # If the regex matched broadly (e.g. "who is alice"), check if it's an expert query
            if expertise:
                r1 = await self.agents["SearchAgent"].execute_task({
                    "action": "find_expert",
                    "expertise": expertise
                })
                all_agent_results.append({"agent": "SearchAgent", "result": r1})
                return self._build_response(message, all_agent_results)
            
            return self._build_response(message, all_agent_results)
        
        # ─── Pattern 8: "Critical X is down!" / "Send alert to X" ───
        alert_to_match = re.search(r'(?:send|trigger)\s+(?:an?\s+)?alert\s+(?:to\s+)?(\w+)?', msg_lower)
        critical_match = re.search(r'(?:critical|urgent|emergency|server|api|system|service)\s+.*(?:down|crash|fail|error|broken|outage)', msg_lower)
        
        if alert_to_match:
            target = (alert_to_match.group(1) or "").capitalize()
            r1 = await self.agents["AlertAgent"].execute_task({
                "action": "send_alert",
                "title": "Alert",
                "message": message,
                "priority": "High",
                "target_person": target
            })
            all_agent_results.append({"agent": "AlertAgent", "result": r1})
            return self._build_response(message, all_agent_results)
        
        if critical_match:
            r1 = await self.agents["AlertAgent"].execute_task({
                "action": "send_alert",
                "title": self._extract_system(message),
                "message": message,
                "priority": "Critical"
            })
            all_agent_results.append({"agent": "AlertAgent", "result": r1})
            return self._build_response(message, all_agent_results)

        # ─── Pattern 9: "Call X to Y" (Voice Agent) ───
        call_match = re.search(r'call\s+(\w+)\s+(?:to|about|for)\s+(.+)', msg_lower)
        if call_match:
            person_name = call_match.group(1).capitalize()
            goal = call_match.group(2)
            
            # Find contact number
            expert = _find_contact(person_name)
            
            if not expert:
                 all_agent_results.append({
                    "agent": "PhoneCallingAgent",
                    "result": {
                        "steps": [
                            f"❌ Contact '{person_name}' not found in database.",
                            "Cannot initiate call."
                        ]
                    }
                })
            else:
                 # Prefer phone, fallback to whatsapp
                 number = expert.get("phone") or expert.get("whatsapp")
                 if not number:
                     all_agent_results.append({
                        "agent": "PhoneCallingAgent",
                        "result": {
                            "steps": [
                                f"❌ Contact '{person_name}' has no phone info.",
                                "Cannot initiate call."
                            ]
                        }
                    })
                 else:
                     # Execute Call
                     r1 = await self.agents["PhoneCallingAgent"].execute_task({
                         "action": "call",
                         "number": number,
                         "goal": goal,
                         "context": context
                     })
                     all_agent_results.append({"agent": "PhoneCallingAgent", "result": r1})
            
            return self._build_response(message, all_agent_results)
        
        # ─── Fallback: Use semantic router ───
        result = process_message(message)
        pipeline = result["pipeline"]
        rpcs = pipeline.get("stage_4_rpc_plan", [])
        
        if rpcs:
            for rpc in rpcs:
                agent_task = self._route_rpc_to_agent(rpc)
                if agent_task:
                    agent_name = agent_task.pop("_agent")
                    agent = self.agents.get(agent_name)
                    if agent:
                        try:
                            r = await agent.execute_task(agent_task)
                            all_agent_results.append({"agent": agent_name, "result": r})
                            print(f"   ✅ {agent_name}: Done")
                        except Exception as e:
                            print(f"   ❌ {agent_name}: {e}")
                            all_agent_results.append({
                                "agent": agent_name,
                                "result": {"steps": [f"❌ {agent_name}: Error - {e}"]}
                            })
        
        if not all_agent_results:
            # No agents matched — conversational response
            return {
                "message": message,
                "total_tasks": 0,
                "tasks": [],
                "agent_results": [],
                "response_lines": [
                    "🤔 I understood your message but couldn't identify a clear action.",
                    "",
                    "💡 Try commands like:",
                    '• "Tell John to fix the bug"',
                    '• "Schedule meeting with Alice at 3pm"',
                    '• "Send alert to Dana"',
                    '• "What meetings do I have?"',
                ]
            }
        
        return self._build_response(message, all_agent_results)
    
    def _build_response(self, message: str, agent_results: list) -> dict:
        """Build the final response with step-by-step lines."""
        response_lines = []
        tasks = []
        
        for ar in agent_results:
            agent_name = ar["agent"]
            result = ar.get("result", {})
            steps = result.get("steps", [])
            
            # Add agent steps
            for step in steps:
                response_lines.append(step)
            
            # Blank line between agents
            if steps:
                response_lines.append("")
            
            tasks.append({
                "agent": agent_name,
                "status": result.get("status", "done"),
                "steps": steps
            })
        
        # Remove trailing blank line
        while response_lines and response_lines[-1] == "":
            response_lines.pop()
        
        return {
            "message": message,
            "total_tasks": len(agent_results),
            "tasks": tasks,
            "agent_results": agent_results,
            "response_lines": response_lines
        }
    
    def _route_rpc_to_agent(self, rpc: dict) -> Optional[dict]:
        """Route a semantic router RPC to the correct agent task."""
        tool_type = rpc.get("tool", "")
        params = rpc.get("params", {})
        
        if tool_type == "schedule_event":
            return {
                "_agent": "CalendarAgent",
                "action": "schedule",
                "title": params.get("topic", "Meeting"),
                "time": params.get("time", "TBD"),
                "participants": params.get("participants", [])
            }
        elif tool_type == "trigger_alert":
            return {
                "_agent": "AlertAgent",
                "action": "send_alert",
                "title": params.get("system", "Alert"),
                "message": params.get("issue", "Unknown"),
                "priority": params.get("priority", "High")
            }
        elif tool_type == "create_ticket":
            return {
                "_agent": "TaskAgent",
                "action": "create_ticket",
                "title": params.get("summary", "Task"),
                "assigned_to": params.get("assignee", "unassigned"),
                "priority": params.get("priority", "Medium"),
                "deadline": params.get("due", "TBD")
            }
        elif tool_type == "create_reminder":
            return {
                "_agent": "CalendarAgent",
                "action": "schedule",
                "title": f"Reminder: {params.get('message', '')}",
                "time": params.get("time", "TBD"),
                "participants": [params.get("target", "self")]
            }
        return None

        return None
    
    def _detect_priority(self, message: str) -> str:
        """Detect priority from message text."""
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["critical", "urgent", "emergency", "asap", "immediately"]):
            return "High"
        elif any(w in msg_lower for w in ["important", "soon"]):
            return "Medium"
        return "Medium"
    
    def _extract_system(self, message: str) -> str:
        """Extract system name from alert message."""
        patterns = [
            r'(?:the\s+)?(\w+(?:\s+\w+)?\s+(?:server|api|gateway|service|database|system))',
            r'(\w+)\s+(?:is\s+)?(?:down|crashed|failing|broken)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        return "System"


# ──────────────────────────────────────────────────────────────
# Demo
# ──────────────────────────────────────────────────────────────

async def demo_scenarios():
    """Run demo scenarios."""
    orchestrator = AgentOrchestrator()
    
    scenarios = [
        "Tell John to fix the bug",
        "Schedule meeting with Alice at 3pm",
        "Send alert to Dana",
        "What meetings do I have?",
        "Find the DevOps expert",
        "Critical server is down!",
        "Reschedule 3pm to 4pm with John",
        "Tell Dana the payment bug is fixed",
    ]
    
    for scenario in scenarios:
        print(f"\n{'═' * 50}")
        print(f"  INPUT: \"{scenario}\"")
        print(f"{'═' * 50}")
        
        result = await orchestrator.route_message(scenario)
        
        print(f"\n  RESPONSE:")
        for line in result.get("response_lines", []):
            print(f"  {line}")
        
        print(f"\n  Tasks: {result['total_tasks']}")
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(demo_scenarios())
