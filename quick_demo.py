#!/usr/bin/env python3
"""Quick step-by-step demo of the multi-agent system."""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multi_agent_system import AgentOrchestrator

async def main():
    print("\n" + "="*70)
    print("⚡ QUICK MULTI-AGENT SYSTEM WALKTHROUGH")
    print("="*70)
    
    # Initialize
    orch = AgentOrchestrator()
    
    # STEP 1: Simple Schedule
    print("\n\n📍 STEP 1: Schedule a meeting")
    print("-" * 70)
    print("User says: 'Schedule meeting Monday 10am with Alice'")
    await orch.route_message("Schedule meeting Monday 10am with Alice")
    cals = json.load(open("data/calendar.json", encoding="utf-8"))
    print(f"✅ Saved to calendar.json ({len(cals)} entries)")
    print(f"   Latest: {cals[-1]['title']} @ {cals[-1]['time']}")
    print()
    
    # STEP 2: Alert & Ticket (2 agents)
    print("📍 STEP 2: Alert the team + Create ticket")
    print("-" * 70)
    print("User says: 'Server down! Alert team. Create ticket for John'")
    await orch.route_message("Server down! Alert team. Create ticket for John")
    
    alts = json.load(open("data/alerts.json", encoding="utf-8"))
    tkts = json.load(open("data/tickets.json", encoding="utf-8"))
    print(f"✅ Alert created ({len(alts)} total)")
    print(f"   {alts[-1]['message'][:50]}...")
    print(f"✅ Ticket created ({len(tkts)} total)")
    print(f"   Assigned to: {tkts[-1].get('assigned_to', 'unassigned')}")
    print()
    
    # STEP 3: Smart delegation with auto-message
    print("📍 STEP 3: Tell Rithvik to reschedule (AUTO-MESSAGE)")
    print("-" * 70)
    print("User says: 'I'm late. Tell Rithvik to reschedule my 2pm'")
    await orch.route_message("I'm late. Tell Rithvik to reschedule my 2pm")
    
    msgs = json.load(open("data/messages.json", encoding="utf-8"))
    print(f"✅ Message auto-generated ({len(msgs)} messages)")
    print(f"\n💬 Smart message sent to {msgs[-1]['to']}:")
    print("-" * 70)
    print(msgs[-1]['message'])
    print("-" * 70)
    print()
    
    # STEP 4: Multi-action (all agents)
    print("📍 STEP 4: Multiple actions in ONE message (WOW!)")
    print("-" * 70)
    print("User says: 'API crashed! Search status, alert team, create ticket for Dana'")
    await orch.route_message("API crashed! Search status, alert team, create ticket for Dana")
    
    alts2 = json.load(open("data/alerts.json", encoding="utf-8"))
    tkts2 = json.load(open("data/tickets.json", encoding="utf-8"))
    searches = []
    if os.path.exists("data/searches.json"):
        searches = json.load(open("data/searches.json", encoding="utf-8"))
    
    print(f"✅ SearchAgent: Monitored ({len(searches)} searches)")
    print(f"✅ AlertAgent: Sent alert ({len(alts2)} alerts total)")
    print(f"✅ TaskAgent: Created ticket ({len(tkts2)} tickets total)")
    print()
    
    # SUMMARY
    print("="*70)
    print("📊 SYSTEM SUMMARY")
    print("="*70)
    
    cals = json.load(open("data/calendar.json", encoding="utf-8"))
    alts = json.load(open("data/alerts.json", encoding="utf-8"))
    tkts = json.load(open("data/tickets.json", encoding="utf-8"))
    msgs = json.load(open("data/messages.json", encoding="utf-8"))
    
    print(f"\n📅 Calendar Events: {len(cals)}")
    print(f"🚨 Alerts: {len(alts)}")
    print(f"🎫 Tickets: {len(tkts)}")
    print(f"💬 Messages: {len(msgs)}")
    
    print("\n✨ KEY FEATURES:")
    print("  ✅ Direct delegation: 'Tell Rithvik to...' → Auto message generated")
    print("  ✅ Multi-action: One message → multiple agents execute")
    print("  ✅ Smart messages: Context-aware, not plain text")
    print("  ✅ Audit trail: All in JSON files (immutable proof)")
    print("  ✅ Async execution: All agents work in parallel")
    
    print("\n🚀 IN TELEGRAM: Same workflow but messages sent to real people")
    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(main())
