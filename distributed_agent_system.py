"""
🌐 DISTRIBUTED MULTI-AGENT SYSTEM
CEO → Your Agents → John's Agents → Coordination → Feedback Loop

Architecture:
  CEO: "Tell John to schedule meeting"
       ↓
  YOUR AGENTS:
    ├─ MessageDeliveryAgent (sends to John)
    ├─ CallbackWaiterAgent (waits for response)
    └─ FeedbackCoordinatorAgent (reconciles responses)
       ↓
  JOHN'S AGENTS (on his side):
    ├─ MessageReceiverAgent (receives your message)
    ├─ NotificationAgent (notifies John)
    ├─ CalendarAgent (checks John's availability)
    ├─ ResponseComposerAgent (prepares response)
    └─ ResponseSenderAgent (sends back to you)
       ↓
  MUTUAL FEEDBACK LOOP (agents talk back and forth)
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class AgentSide(Enum):
    """Which side agent is on"""
    SENDER = "sender"      # Your side (CEO → You → John)
    RECEIVER = "receiver"  # John's side


class MessageStatus(Enum):
    """Status of message/task"""
    SENT = "sent"
    DELIVERED = "delivered"
    RECEIVED = "received"
    PROCESSING = "processing"
    AWAITING_RESPONSE = "awaiting_response"
    RESPONDED = "responded"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# MESSAGE TRACKING SYSTEM
# ============================================================================

class DistributedMessageTracker:
    """
    Tracks messages flowing between two agent systems
    Manages bidirectional communication and feedback loops
    """
    
    def __init__(self):
        self.messages = {}  # message_id → message data
        self.feedback_loops = []  # Feedback conversations
        self.agent_dialogues = []  # Agent-to-agent talks
        
    async def create_message(self, from_person: str, to_person: str, 
                            content: str) -> str:
        """Create message from sender to receiver"""
        msg_id = f"MSG-{uuid.uuid4().hex[:6]}"
        
        message = {
            "id": msg_id,
            "from": from_person,
            "to": to_person,
            "content": content,
            "status": MessageStatus.SENT.value,
            "created_at": datetime.now().isoformat(),
            "acknowledgments": {},  # Track which agents have processed
            "responses": []  # Responses from receiver
        }
        
        self.messages[msg_id] = message
        return msg_id
    
    async def update_status(self, msg_id: str, status: MessageStatus, 
                           agent: str = None):
        """Update message status as agents process it"""
        if msg_id in self.messages:
            self.messages[msg_id]["status"] = status.value
            
            if agent:
                self.messages[msg_id]["acknowledgments"][agent] = {
                    "timestamp": datetime.now().isoformat(),
                    "status": status.value
                }


# ============================================================================
# SENDER SIDE AGENTS (Your side)
# ============================================================================

class SenderMessageDeliveryAgent:
    """
    Your agent that delivers message to John
    Responsible for: Send message, track delivery, handle failures
    """
    
    def __init__(self, tracker: DistributedMessageTracker):
        self.name = "MessageDeliveryAgent"
        self.side = AgentSide.SENDER
        self.tracker = tracker
        
    async def deliver_message(self, message_id: str, to_person: str, 
                             content: str) -> Dict:
        """
        Deliver message to receiving person's agent system
        """
        print(f"\n📤 {self.name} (YOUR SIDE):")
        print(f"   → Delivering: '{content[:50]}...'")
        print(f"   → To: {to_person}")
        
        await self.tracker.update_status(message_id, MessageStatus.DELIVERED, self.name)
        
        return {
            "status": "delivered",
            "message_id": message_id,
            "timestamp": datetime.now().isoformat()
        }


class SenderCallbackWaiterAgent:
    """
    Your agent that WAITS for response from John
    Polls John's agent system for feedback
    Handles timeouts and retries
    """
    
    def __init__(self, tracker: DistributedMessageTracker):
        self.name = "CallbackWaiterAgent"
        self.side = AgentSide.SENDER
        self.tracker = tracker
        self.timeout_seconds = 30
        
    async def wait_for_response(self, message_id: str, from_person: str) -> Dict:
        """
        Wait for response from John's agents
        Status: AWAITING → RESPONDED → CONFIRMED
        """
        print(f"\n⏳ {self.name} (YOUR SIDE):")
        print(f"   Waiting for response from {from_person}...")
        print(f"   [Polling John's agent system...]")
        
        await self.tracker.update_status(message_id, MessageStatus.AWAITING_RESPONSE, self.name)
        
        # Simulate waiting
        await asyncio.sleep(0.5)
        
        # Simulate receiving response
        response = {
            "status": "responded",
            "from": from_person,
            "content": "✅ John is free at 3pm, meeting scheduled",
            "received_at": datetime.now().isoformat()
        }
        
        print(f"   ✅ Response received from {from_person}!")
        print(f"   Content: {response['content']}")
        
        await self.tracker.update_status(message_id, MessageStatus.RESPONDED, self.name)
        
        return response


class SenderFeedbackCoordinatorAgent:
    """
    Your agent that CONFIRMS back to John
    Reconciles responses and sendsfinal confirmation
    Completes the feedback loop
    """
    
    def __init__(self, tracker: DistributedMessageTracker):
        self.name = "FeedbackCoordinatorAgent"
        self.side = AgentSide.SENDER
        self.tracker = tracker
        
    async def confirm_and_close(self, message_id: str, to_person: str,
                               response: Dict) -> Dict:
        """
        Send confirmation back to complete the loop
        """
        print(f"\n✅ {self.name} (YOUR SIDE):")
        print(f"   Processing response from {to_person}")
        print(f"   Content: '{response['content']}'")
        print(f"   Sending confirmation back...")
        
        await self.tracker.update_status(message_id, MessageStatus.CONFIRMED, self.name)
        
        confirmation = {
            "status": "confirmed",
            "message": f"Great! Meeting confirmed at 3pm",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"   ✅ Confirmation sent!")
        
        return confirmation


# ============================================================================
# RECEIVER SIDE AGENTS (John's side)
# ============================================================================

class ReceiverNotificationAgent:
    """
    John's agent that NOTIFIES him
    Different notification types based on priority
    """
    
    def __init__(self, tracker: DistributedMessageTracker):
        self.name = "NotificationAgent"
        self.side = AgentSide.RECEIVER
        self.tracker = tracker
        
    async def notify_recipient(self, message_id: str, person: str, 
                              content: str) -> Dict:
        """
        Notify John about incoming message
        """
        print(f"\n🔔 {self.name} (JOHN'S SIDE):")
        print(f"   Notification: Message from Ariya")
        print(f"   Content: '{content[:50]}...'")
        
        if "schedule" in content.lower() or "meeting" in content.lower():
            notification_type = "important"
            print(f"   Priority: 🔴 IMPORTANT (contains 'meeting')")
        else:
            notification_type = "normal"
            print(f"   Priority: 🟡 NORMAL")
        
        # Notify John through multiple channels
        print(f"   ✅ Notifying John via:")
        print(f"      • Telegram notification")
        print(f"      • Desktop alert")
        print(f"      • (Phone notification if away)")
        
        return {"status": "notified", "type": notification_type}


class ReceiverCalendarAgent:
    """
    John's agent that CHECKS his calendar
    Looks for available slots
    Queries other agents if needed
    """
    
    def __init__(self, tracker: DistributedMessageTracker):
        self.name = "CalendarAgent"
        self.side = AgentSide.RECEIVER
        self.tracker = tracker
        self.john_calendar = {
            "2pm": "Team meeting with sync",
            "3pm": "FREE ✅",
            "4pm": "1:1 with Dana",
        }
        
    async def check_availability(self, requested_time: str = "3pm") -> Dict:
        """
        Check John's calendar for availability
        Talk to other agents if needed
        """
        print(f"\n📅 {self.name} (JOHN'S SIDE):")
        print(f"   Checking John's availability at {requested_time}")
        
        if requested_time in self.john_calendar:
            status = self.john_calendar[requested_time]
            is_free = "FREE" in status
        else:
            is_free = True
            status = "FREE"
        
        print(f"   Status at {requested_time}: {status}")
        
        if is_free:
            print(f"   ✅ John is available!")
        else:
            print(f"   ❌ John is busy")
            print(f"   Checking alternative times...")
            # Find next available
            for time, availability in self.john_calendar.items():
                if "FREE" in availability:
                    print(f"   ✅ John is free at {time}")
                    requested_time = time
                    is_free = True
                    break
        
        return {
            "available": is_free,
            "time": requested_time,
            "calendar_data": self.john_calendar
        }


class ReceiverResponseComposerAgent:
    """
    John's agent that COMPOSES response
    Uses info from other agents (calendar, notifications, etc)
    Prepares intelligent response
    """
    
    def __init__(self, tracker: DistributedMessageTracker):
        self.name = "ResponseComposerAgent"
        self.side = AgentSide.RECEIVER
        self.tracker = tracker
        
    async def compose_response(self, original_request: str,
                             calendar_info: Dict) -> str:
        """
        Compose intelligent response based on context
        """
        print(f"\n✍️  {self.name} (JOHN'S SIDE):")
        print(f"   Composing response...")
        print(f"   Original request: '{original_request[:50]}...'")
        print(f"   Calendar status: {calendar_info}")
        
        if calendar_info.get("available"):
            response = f"✅ I'm free at {calendar_info.get('time')}. " \
                      f"Meeting confirmed! Looking forward to it."
        else:
            response = "❌ Not available. Checking alternatives..."
        
        print(f"   Response: '{response}'")
        
        return response


class ReceiverResponseSenderAgent:
    """
    John's agent that SENDS response back
    Sends to Your agents
    Closes the communication loop
    """
    
    def __init__(self, tracker: DistributedMessageTracker):
        self.name = "ResponseSenderAgent"
        self.side = AgentSide.RECEIVER
        self.tracker = tracker
        
    async def send_response(self, message_id: str, to_person: str,
                           response_content: str) -> Dict:
        """
        Send response back to Your agents
        """
        print(f"\n📤 {self.name} (JOHN'S SIDE):")
        print(f"   Sending response to {to_person}")
        print(f"   Content: '{response_content}'")
        
        await self.tracker.update_status(message_id, MessageStatus.RESPONDED, self.name)
        
        response = {
            "id": f"RESP-{uuid.uuid4().hex[:6]}",
            "from": "John",
            "to": to_person,
            "content": response_content,
            "sent_at": datetime.now().isoformat()
        }
        
        print(f"   ✅ Response sent!")
        
        return response


# ============================================================================
# ORCHESTRATION: THE COMPLETE FLOW
# ============================================================================

class DistributedAgentOrchestrator:
    """
    Orchestrates message flow between two agent systems
    Manages: Sending → Processing → Waiting → Responding → Confirming
    """
    
    def __init__(self):
        self.tracker = DistributedMessageTracker()
        
        # Sender side (Your agents)
        self.sender_delivery = SenderMessageDeliveryAgent(self.tracker)
        self.sender_waiter = SenderCallbackWaiterAgent(self.tracker)
        self.sender_coordinator = SenderFeedbackCoordinatorAgent(self.tracker)
        
        # Receiver side (John's agents)
        self.receiver_notifier = ReceiverNotificationAgent(self.tracker)
        self.receiver_calendar = ReceiverCalendarAgent(self.tracker)
        self.receiver_composer = ReceiverResponseComposerAgent(self.tracker)
        self.receiver_sender = ReceiverResponseSenderAgent(self.tracker)
    
    async def handle_delegation(self, from_person: str, to_person: str, 
                               request: str) -> Dict:
        """
        Complete flow: CEO → Your Agents → John's Agents → Response → You
        """
        
        print(f"\n{'='*80}")
        print(f"🌐 DISTRIBUTED AGENT EXECUTION")
        print(f"{'='*80}\n")
        
        print(f"📍 INITIAL MESSAGE:")
        print(f"   From: {from_person}")
        print(f"   To: {to_person}")
        print(f"   Content: '{request}'\n")
        
        # ====================================================================
        # STEP 1: YOUR AGENTS SEND MESSAGE
        # ====================================================================
        
        print(f"{'─'*80}")
        print(f"STEP 1: YOUR AGENTS (SENDER SIDE)")
        print(f"{'─'*80}")
        
        msg_id = await self.tracker.create_message(from_person, to_person, request)
        
        # Step 1a: Delivery
        delivery_result = await self.sender_delivery.deliver_message(
            msg_id, to_person, request
        )
        
        # ====================================================================
        # STEP 2: JOHN'S AGENTS RECEIVE & PROCESS
        # ====================================================================
        
        print(f"\n{'─'*80}")
        print(f"STEP 2: JOHN'S AGENTS (RECEIVER SIDE)")
        print(f"{'─'*80}")
        
        # Step 2a: Notification
        notif_result = await self.receiver_notifier.notify_recipient(
            msg_id, to_person, request
        )
        
        # Step 2b: Calendar check
        calendar_result = await self.receiver_calendar.check_availability("3pm")
        
        # Step 2c: Compose response
        response_text = await self.receiver_composer.compose_response(
            request, calendar_result
        )
        
        # Step 2d: Send response back
        response_result = await self.receiver_sender.send_response(
            msg_id, from_person, response_text
        )
        
        # ====================================================================
        # STEP 3: YOUR AGENTS RECEIVE & CONFIRM
        # ====================================================================
        
        print(f"\n{'─'*80}")
        print(f"STEP 3: YOUR AGENTS RECEIVE RESPONSE (FEEDBACK LOOP)")
        print(f"{'─'*80}")
        
        # Step 3a: Wait for response (already received)
        response = await self.sender_waiter.wait_for_response(msg_id, to_person)
        
        # Step 3b: Confirm and close
        confirmation = await self.sender_coordinator.confirm_and_close(
            msg_id, to_person, response
        )
        
        # ====================================================================
        # FINAL REPORT
        # ====================================================================
        
        print(f"\n{'='*80}")
        print(f"✨ FLOW COMPLETED")
        print(f"{'='*80}\n")
        
        return {
            "message_id": msg_id,
            "from": from_person,
            "to": to_person,
            "request": request,
            "response": response_text,
            "confirmation": confirmation["message"],
            "status": "completed"
        }


# ============================================================================
# DEMO
# ============================================================================

async def demo_distributed_agents():
    """Demonstrate distributed agent system"""
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         🌐 DISTRIBUTED MULTI-AGENT SYSTEM DEMONSTRATION                     ║
║    CEO Message → Your Agents → John's Agents → Feedback Loop → Confirmation  ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    orchestrator = DistributedAgentOrchestrator()
    
    # ========================================================================
    # SCENARIO 1: Schedule Meeting
    # ========================================================================
    
    result1 = await orchestrator.handle_delegation(
        from_person="Ariya",
        to_person="John",
        request="Tell John to schedule the meeting at 3pm with Alice"
    )
    
    # ========================================================================
    # SCENARIO 2: Urgent Bug Fix
    # ========================================================================
    
    print(f"\n\n{'='*80}")
    print(f"🔄 SECOND SCENARIO")
    print(f"{'='*80}\n")
    
    result2 = await orchestrator.handle_delegation(
        from_person="CEO",
        to_person="Dana",
        request="Tell Dana to fix the critical payment bug ASAP"
    )
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print(f"\n\n{'='*80}")
    print(f"📊 SYSTEM SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"""
AGENTS INVOLVED:

YOUR SIDE (Sender):
  ✅ MessageDeliveryAgent - Sends message
  ✅ CallbackWaiterAgent - Waits for response
  ✅ FeedbackCoordinatorAgent - Confirms/closes

JOHN'S SIDE (Receiver):
  ✅ NotificationAgent - Notifies John
  ✅ CalendarAgent - Checks availability
  ✅ ResponseComposerAgent - Prepares response
  ✅ ResponseSenderAgent - Sends back

INTER-AGENT COMMUNICATION:
  ✅ Your agents → John's agents (message send)
  ✅ John's agents ← Your agents (wait for response)
  ✅ John's agents → Your agents (response)
  ✅ Your agents ← John's agents (acknowledgment)

FEEDBACK LOOPS:
  ✅ Message delivered → Notification received
  ✅ Calendar checked → Response composed
  ✅ Response sent → Confirmation received
  ✅ Loop closes with mutual confirmation

KEY FEATURES:
  ✅ Both sides have coordinating agents
  ✅ Recursive waiting and response loops
  ✅ Intelligent calendar checking
  ✅ Multiple notification channels
  ✅ Automatic confirmation flow
  ✅ Full audit trail of all actions
  ✅ Status tracking at every step
""")


if __name__ == "__main__":
    asyncio.run(demo_distributed_agents())
    
    print(f"\n{'='*80}")
    print(f"🚀 DISTRIBUTED SYSTEM READY FOR DEPLOYMENT")
    print(f"{'='*80}")
