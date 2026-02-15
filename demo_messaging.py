#!/usr/bin/env python3
"""
DEMO: Multi-Agent Messaging System
Shows how the system works without Telegram connection
"""

import asyncio
import json
import os
from datetime import datetime

# Add imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system import AgentOrchestrator

async def demo():
    """Demo the multi-agent messaging system."""
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(telegram_bot=None)
    
    print("\n" + "="*70)
    print("🤖 MULTI-AGENT MESSAGING SYSTEM DEMO")
    print("="*70)
    
    # Demo 1: Delegation with smart message generation
    print("\n📱 USER MESSAGE 1:")
    print("  'I'm late to my 2pm meeting. Tell Rithvik to reschedule it.'")
    
    result = await orchestrator.route_message("I'm late to my 2pm meeting. Tell Rithvik to reschedule it.")
    
    print(f"\n✅ Result:")
    for task in result.get("execution_results", []):
        agent = task.get("agent")
        res = task.get("result", {})
        print(f"   {agent}: {res.get('message', res.get('status'))}")
    
    # Show generated message
    messages = json.loads(open("data/messages.json", encoding="utf-8").read())
    if messages:
        last_msg = messages[-1]
        print(f"\n💬 SMART MESSAGE SENT TO RITHVIK:")
        print("   " + "─"*60)
        print(f"{last_msg['message']}")
        print("   " + "─"*60)
    
    await asyncio.sleep(1)
    
    # Demo 2: Urgent alert with auto-message
    print("\n\n📱 USER MESSAGE 2:")
    print("  'The payment API is down! Alert the team. Contact John to fix it.'")
    
    result = await orchestrator.route_message("The payment API is down! Alert the team. Contact John to fix it.")
    
    print(f"\n✅ Result:")
    for task in result.get("execution_results", []):
        agent = task.get("agent")
        res = task.get("result", {})
        print(f"   {agent}: {res.get('message', res.get('status'))}")
    
    # Check data files
    print("\n\n📊 DATA GENERATED:")
    
    files = ["messages.json", "alerts.json", "tickets.json"]
    for fname in files:
        fpath = f"data/{fname}"
        if os.path.exists(fpath):
            data =json.loads(open(fpath, encoding="utf-8").read())
            print(f"\n{fname}: {len(data)} entries")
            if data:
                last_entry = data[-1]
                print(f"  Latest: {list(last_entry.keys())}")
                if "message" in last_entry:
                    preview = last_entry["message"][:60]
                    print(f"  Preview: {preview}...")


if __name__ == "__main__":
    asyncio.run(demo())
