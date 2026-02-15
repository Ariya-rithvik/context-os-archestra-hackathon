"""
🗣️ AGENT COMMUNICATION MODES
Agents can talk to users directly via Telegram
"""

from enum import Enum
from datetime import datetime

class CommunicationMode(Enum):
    """How agents communicate with users"""
    SILENT = "silent"              # Process only, no response
    CONVERSATIONAL = "conversational"  # Respond to user
    VERBOSE = "verbose"            # Detailed explanations


class AgentCommunicator:
    """Agent can speak directly to user"""
    
    def __init__(self, mode: CommunicationMode = CommunicationMode.CONVERSATIONAL):
        self.mode = mode
        self.conversation_history = []
    
    async def respond_to_user(self, user: str, action: str, details: dict = None):
        """
        Agent sends response directly back to user via Telegram
        """
        if self.mode == CommunicationMode.SILENT:
            return self._log_silently(action, details)
        
        elif self.mode == CommunicationMode.CONVERSATIONAL:
            return self._respond_friendly(user, action, details)
        
        elif self.mode == CommunicationMode.VERBOSE:
            return self._respond_detailed(user, action, details)
    
    def _log_silently(self, action: str, details: dict = None):
        """Just log, don't respond (current behavior)"""
        print(f"  🤐 Silent mode: {action}")
        return None
    
    def _respond_friendly(self, user: str, action: str, details: dict = None):
        """
        Friendly response back to user
        Example: "✅ Got it! I've sent message to John"
        """
        responses = {
            "schedule_created": f"✅ Got it! I've scheduled the meeting for {details.get('time', 'that time')}",
            "alert_sent": f"🚨 Alert sent! Team notified (priority: {details.get('priority', 'medium')})",
            "ticket_created": f"🎫 Ticket created! Assigned to {details.get('assigned_to', 'person')}",
            "message_sent": f"📨 Message sent to {details.get('to', 'person')} via {details.get('channel', 'their channel')}",
            "search_complete": f"🔍 Search complete! Found {details.get('count', '0')} results",
        }
        
        response = responses.get(action, f"✅ Done! {action}")
        
        print(f"\n📱 AGENT RESPONSE TO USER ({user}):")
        print(f"   {response}")
        print()
        
        self.conversation_history.append({
            "type": "agent_response",
            "user": user,
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _respond_detailed(self, user: str, action: str, details: dict = None):
        """
        Verbose response with full explanation
        Example shows all agent reasoning
        """
        print(f"\n🤖 DETAILED AGENT REPORT FOR {user}")
        print(f"{'='*60}")
        
        if action == "message_sent":
            print(f"✅ Task: Send message to {details.get('to')}")
            print(f"   Contact found: ✅")
            print(f"   Activity checked: 🟢 {details.get('activity', 'Active on Slack')}")
            print(f"   Route chosen: {details.get('channel', 'Slack')}")
            print(f"   Message status: {details.get('status', 'Sent')}")
            print(f"\n   📝 Message sent:")
            print(f"   \"{details.get('message_content', '')[:50]}...\"")
        
        elif action == "ticket_created":
            print(f"✅ Task: Create ticket for {details.get('assigned_to')}")
            print(f"   Ticket ID: {details.get('ticket_id', 'TKT-001')}")
            print(f"   Priority: {details.get('priority', 'Medium')}")
            print(f"   Description: {details.get('description', '')[:50]}...")
        
        elif action == "alert_sent":
            print(f"🚨 Alert sent to team")
            print(f"   Priority: {details.get('priority', 'Medium')}")
            print(f"   Recipients notified: {details.get('recipient_count', '5')}")
        
        print(f"{'='*60}\n")
        
        return f"Detailed report printed above ☝️"


# ============================================================================
# AGENT-TO-AGENT COMMUNICATION
# ============================================================================

class AgentCollaboration:
    """Agents can talk to EACH OTHER"""
    
    def __init__(self):
        self.agent_messages = []
        self.task_queue = []
    
    async def agent_asks_another(self, asking_agent: str, asked_agent: str, 
                                  question: str) -> str:
        """
        Agent A asks Agent B for information
        Example: MessagingAgent asks CalendarAgent "When is John's next meeting?"
        """
        print(f"\n🗣️ INTER-AGENT COMMUNICATION")
        print(f"   {asking_agent}Agent → {asked_agent}Agent")
        print(f"   Question: {question}")
        
        # Agent B responds
        response = await self._get_agent_response(asked_agent, question)
        
        print(f"   Answer: {response}")
        print()
        
        self.agent_messages.append({
            "from": asking_agent,
            "to": asked_agent,
            "question": question,
            "answer": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    async def _get_agent_response(self, agent_name: str, question: str) -> str:
        """Simulate agent response"""
        responses = {
            "calendar": "John's next meeting is Monday 2pm with Alice",
            "task": "John has 3 open tickets",
            "alert": "No critical alerts for John",
            "search": "Found 2 recent updates about John's project",
        }
        
        for key, response in responses.items():
            if key in agent_name.lower():
                return response
        
        return "No information available"
    
    async def delegate_subtask(self, current_agent: str, target_agent: str, 
                               task: str) -> dict:
        """
        Agent delegates a subtask to another agent
        Example: TaskAgent says to MessagingAgent "Send message to John about deadline"
        """
        print(f"\n📋 AGENT-TO-AGENT TASK DELEGATION")
        print(f"   From: {current_agent}Agent")
        print(f"   To: {target_agent}Agent")
        print(f"   Task: {task}")
        
        result = {
            "delegated_to": target_agent,
            "task": task,
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        }
        
        self.task_queue.append(result)
        
        # Simulate task completion
        import asyncio
        await asyncio.sleep(0.5)
        
        result["status"] = "completed"
        print(f"   Status: ✅ Completed")
        print()
        
        return result


# ============================================================================
# DEMONSTRATION
# ============================================================================

async def demo_communication_modes():
    """Show different ways agents can talk"""
    
    print(f"\n{'='*70}")
    print(f"🗣️  AGENT COMMUNICATION MODES DEMONSTRATION")
    print(f"{'='*70}\n")
    
    # ========================================================================
    # MODE 1: SILENT
    # ========================================================================
    print(f"\n{'─'*70}")
    print(f"MODE 1: SILENT (Current system)")
    print(f"{'─'*70}")
    print(f"User: 'Tell John to fix the bug'\n")
    
    silent_agent = AgentCommunicator(CommunicationMode.SILENT)
    await silent_agent.respond_to_user(
        user="Ariya",
        action="message_sent",
        details={
            "to": "John",
            "channel": "Slack",
            "status": "success"
        }
    )
    
    # ========================================================================
    # MODE 2: CONVERSATIONAL
    # ========================================================================
    print(f"\n{'─'*70}")
    print(f"MODE 2: CONVERSATIONAL (Agent responds to user)")
    print(f"{'─'*70}")
    print(f"User: 'Tell John to fix the bug'\n")
    
    friendly_agent = AgentCommunicator(CommunicationMode.CONVERSATIONAL)
    response = await friendly_agent.respond_to_user(
        user="Ariya",
        action="message_sent",
        details={
            "to": "John",
            "channel": "Slack",
            "status": "success"
        }
    )
    
    # ========================================================================
    # MODE 3: VERBOSE
    # ========================================================================
    print(f"\n{'─'*70}")
    print(f"MODE 3: VERBOSE (Full agent explanation)")
    print(f"{'─'*70}")
    print(f"User: 'Tell John to fix the bug'\n")
    
    verbose_agent = AgentCommunicator(CommunicationMode.VERBOSE)
    await verbose_agent.respond_to_user(
        user="Ariya",
        action="message_sent",
        details={
            "to": "John",
            "channel": "Slack",
            "activity": "Active on Slack (2 mins ago)",
            "message_content": "Tell John to fix the critical bug ASAP"
        }
    )
    
    # ========================================================================
    # INTER-AGENT COMMUNICATION
    # ========================================================================
    print(f"\n{'─'*70}")
    print(f"AGENTS TALKING TO EACH OTHER")
    print(f"{'─'*70}\n")
    
    collaboration = AgentCollaboration()
    
    # Agent asking another agent
    await collaboration.agent_asks_another(
        asking_agent="Messaging",
        asked_agent="Calendar",
        question="When is John's next meeting?"
    )
    
    await collaboration.agent_asks_another(
        asking_agent="Task",
        asked_agent="Alert",
        question="Are there any critical issues right now?"
    )
    
    # Agent delegating to another
    await collaboration.delegate_subtask(
        current_agent="Task",
        target_agent="Messaging",
        task="Send deadline reminder to John"
    )
    
    # ========================================================================
    # COMPLEX SCENARIO: Full conversation
    # ========================================================================
    print(f"\n{'='*70}")
    print(f"COMPLETE SCENARIO: User → Agents → User Response")
    print(f"{'='*70}\n")
    
    print(f"USER SAYS in Telegram:")
    print(f"  'I'm late for the 2pm meeting. Tell Rithvik to reschedule to 3pm'\n")
    
    conv_agent = AgentCommunicator(CommunicationMode.CONVERSATIONAL)
    
    print(f"AGENTS WORK (Behind the scenes):")
    print(f"  1. CalendarAgent: Detects scheduling issue")
    print(f"  2. MessagingAgent: Detects delegation to Rithvik")
    print(f"  3. TaskAgent: Creates reminder task")
    print(f"  4. MessagingAgent asks CalendarAgent: 'What meetings does user have?'")
    
    await collaboration.agent_asks_another(
        asking_agent="Messaging",
        asked_agent="Calendar",
        question="What does the user have scheduled at 2pm?"
    )
    
    print(f"\nAGENT RESPONDS TO USER in Telegram:")
    response = await conv_agent.respond_to_user(
        user="Ariya",
        action="message_sent",
        details={
            "to": "Rithvik",
            "channel": "Slack",
            "status": "success"
        }
    )
    
    print(f"USER SEES in Telegram:")
    print(f"  ✅ Message sent to Rithvik via Slack")
    print(f"  📅 Your 2pm meeting has been marked as late")
    print(f"\nUSER SEES in Slack:")
    print(f"  [From Agent]: 'I'm late for the 2pm meeting. Please reschedule to 3pm'")
    print(f"  To: @rithvik")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_communication_modes())
    
    print(f"\n{'='*70}")
    print(f"✨ SUMMARY")
    print(f"{'='*70}")
    print(f"""
Agents CAN talk directly:

1️⃣ TO USERS (Via Telegram):
   ✅ Silent mode: Process only (current)
   ✅ Conversational: Quick responses
   ✅ Verbose: Full explanations

2️⃣ TO EACH OTHER:
   ✅ Ask questions: "Calendar: When is John's next meeting?"
   ✅ Delegate tasks: "Task, please complete this for me"
   ✅ Share information: "Alert: Server is down!"
   ✅ Collaborate: Work together on complex tasks

3️⃣ CURRENT SYSTEM:
   Mode: CONVERSATIONAL (can be changed)
   Agents respond to users in Telegram
   Agents coordinate with each other
   All conversations logged in messages.json

Next steps:
  → Enable conversation mode in telegram_bot.py
  → Agents will talk back to users!
""")
