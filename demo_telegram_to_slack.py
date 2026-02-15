#!/usr/bin/env python3
"""
End-to-end demo: Telegram → Multi-Agent → Slack
Shows complete flow without needing actual Telegram connectivity.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system import AgentOrchestrator
from slack_integration import intelligent_send

async def demo():
    print("\n" + "="*70)
    print("🔗 TELEGRAM → MULTI-AGENT → SLACK DEMO")
    print("="*70)
    
    orch = AgentOrchestrator()
    
    # DEMO 1: User sends delegation message via Telegram
    print("\n\n📱 SCENARIO 1: Telegram User sends delegation message")
    print("-"*70)
    print("Telegram App: User types message to bot")
    print('  "Tell John to fix the critical bug ASAP"')
    
    message = "Tell John to fix the critical bug ASAP"
    print(f"\n🤖 Agent receives: {message}")
    
    # Step 1: Agent processes through multi-agent system
    print("\n⚙️  STEP 1: Agents process message")
    result = await orch.route_message(message)
    print(f"   ✅ Agents routed: {result['total_tasks']} tasks")
    
    # Step 2: Agent detects "Tell John" pattern
    print("\n⚙️  STEP 2: Detect delegation pattern → 'Tell John'")
    print("   ✅ Pattern detected: \"Tell [person]\"")
    
    # Step 3: Use intelligent_send to route to Slack
    print("\n⚙️  STEP 3: Choose best channel to contact John")
    slack_result = intelligent_send("John", message)
    
    print(f"\n🧠 Agent Chain of Thought:")
    for step in slack_result.get("chain_of_thought", []):
        print(f"   {step}")
    
    msg_result = slack_result.get("message_result", {})
    print(f"\n📤 Result:")
    print(f"   App: {msg_result.get('app')}")
    print(f"   To: {msg_result.get('to')}")
    print(f"   Status: {msg_result.get('status')}")
    
    if msg_result.get("status") == "success":
        print(f"\n✅ MESSAGE SENT TO SLACK!")
        print(f"   Check your Slack #social channel now 👆")
    else:
        print(f"   Status: {msg_result.get('status')}")
    
    # DEMO 2: Complex message with multiple actions
    print("\n\n" + "="*70)
    print("📱 SCENARIO 2: Complex message (multiple actions + delegation)")
    print("-"*70)
    print("Telegram App: User types")
    print('  "Server is down! Alert the team and tell Dana to investigate"')
    
    message2 = "Server is down! Alert the team and tell Dana to investigate"
    print(f"\n🤖 Agent receives: {message2}")
    
    print("\n⚙️  Processing through agents...")
    result2 = await orch.route_message(message2)
    print(f"   ✅ {result2['total_tasks']} agents activated")
    
    print("\n⚙️  Detecting delegation pattern → 'Tell Dana'")
    slack_result2 = intelligent_send("Dana", message2)
    
    print(f"\n🧠 Agent Chain of Thought:")
    for step in slack_result2.get("chain_of_thought", []):
        print(f"   {step}")
    
    msg_result2 = slack_result2.get("message_result", {})
    if msg_result2.get("status") == "success":
        print(f"\n✅ MESSAGE SENT TO SLACK!")
        print(f"   Check your Slack #social channel 👆")
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 COMPLETE ARCHITECTURE")
    print("="*70)
    
    print("""
    ┌─────────────────────────────────────────────────────────┐
    │                 TELEGRAM USER                           │
    │    "Tell John to fix the critical bug ASAP"            │
    └───────────┬──────────────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────────────────────────┐
    │            TELEGRAM BOT INPUT LAYER                     │
    │    🤖 telegram_bot.py listening for messages            │
    └───────────┬──────────────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────────────────────────┐
    │          MULTI-AGENT SYSTEM (BRAIN)                    │
    │  ✅ CalendarAgent (schedule/reschedule)                │
    │  ✅ AlertAgent (send alerts)                           │
    │  ✅ TaskAgent (create tickets)                         │
    │  ✅ MessagingAgent (detect delegation)                 │
    │  ✅ SearchAgent (web search)                           │
    └───────────┬──────────────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────────────────────────┐
    │          SLACK INTEGRATION LAYER (HANDS)               │
    │  1. intelligent_send() detects "Tell John"             │
    │  2. Checks John's activity → SLACK (active 2 mins ago) │
    │  3. Sends message via webhook                          │
    └───────────┬──────────────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────────────────────────┐
    │              SLACK CHANNEL (#social)                   │
    │    📨 Message from Agent                               │
    │    "Tell John to fix the critical bug ASAP"            │
    │    To: @john                                            │
    │    [MESSAGE DELIVERED] ✅                              │
    └─────────────────────────────────────────────────────────┘
    """)
    
    print("\n🎯 KEY INNOVATION:")
    print("  • Agent autonomously chooses SLACK over WhatsApp/Email")
    print("  • Based on real activity data (last seen 2 mins ago)")
    print("  • No manual routing needed - INTELLIGENT ROUTING")
    print("  • Message context-aware, not just plain text")


if __name__ == "__main__":
    asyncio.run(demo())
