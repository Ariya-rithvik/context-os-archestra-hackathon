"""
ContextOS - Semantic Router
Demonstrates the semantic intelligence pipeline that Archestra handles in production.

Pipeline: Raw Text → Extract Actions → Classify Intent → Resolve Context → Plan RPCs

This is a standalone demo showing how natural language gets compiled
into structured RPC calls. Run directly: python semantic_router.py
"""

import re
from datetime import datetime, timedelta
from typing import Optional


# ──────────────────────────────────────────────
# Stage 1: Semantic Extraction
# ──────────────────────────────────────────────
# Keyword patterns that map to action types
ACTION_PATTERNS = {
    "SCHEDULE_EVENT": {
        "keywords": ["meeting", "sync", "call", "standup", "post-mortem", "catch-up",
                      "schedule", "book", "set up", "arrange"],
        "description": "Calendar event detected"
    },
    "TRIGGER_ALERT": {
        "keywords": ["error", "down", "fail", "broken", "500", "outage", "crash",
                      "alert", "urgent", "critical", "emergency"],
        "description": "DevOps alert detected"
    },
    "CREATE_TICKET": {
        "keywords": ["fix", "task", "assign", "ticket", "jira", "action item",
                      "revert", "update", "implement", "build", "deploy"],
        "description": "Task ticket detected"
    },
    "CREATE_REMINDER": {
        "keywords": ["remind", "don't forget", "follow up", "check back",
                      "ping me", "remember", "later"],
        "description": "Reminder detected"
    }
}

# Priority keywords
PRIORITY_MAP = {
    "high": ["urgent", "critical", "emergency", "asap", "immediately", "high"],
    "medium": ["soon", "when possible", "medium", "moderate"],
    "low": ["eventually", "low", "whenever", "no rush"]
}

# Time-related patterns
TIME_PATTERNS = [
    r'\b(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))\b',
    r'\b(tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\b(next\s+(?:week|monday|tuesday|wednesday|thursday|friday))\b',
    r'\b(in\s+\d+\s+(?:hours?|minutes?|days?))\b',
    r'\b(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b',
    r'\b(end\s+of\s+(?:day|week))\b',
    r'\b(morning|afternoon|evening)\b'
]

# Person/team patterns
PERSON_PATTERNS = [
    r'@(\w+)',
    r'\b(?:with|to|for|assign(?:ed)?\s+to)\s+(?:the\s+)?(\w+(?:-\w+)?(?:\s+team)?)\b'
]


def extract_actions(text: str) -> list[dict]:
    """
    Stage 1: Extract structured actions from raw text.
    Uses keyword matching to identify action types.
    """
    text_lower = text.lower()
    actions = []

    for action_type, config in ACTION_PATTERNS.items():
        matched_keywords = [kw for kw in config["keywords"] if kw in text_lower]
        if matched_keywords:
            actions.append({
                "type": action_type,
                "matched_keywords": matched_keywords,
                "description": config["description"],
                "raw_text": text
            })

    return actions


# ──────────────────────────────────────────────
# Stage 2: Intent Classification
# ──────────────────────────────────────────────
INTENT_TYPES = ["COMMAND", "INFORMATION", "DISCUSSION", "SUGGESTION"]


def classify_intent(text: str, actions: list[dict]) -> dict:
    """
    Stage 2: Classify the overall message intent.
    Only COMMAND intent triggers execution.
    """
    text_lower = text.lower()

    # Command indicators
    command_signals = ["please", "can you", "do", "make", "set", "create",
                       "send", "trigger", "schedule", "book", "assign",
                       "tell", "alert", "notify", "remind"]
    # Question indicators
    question_signals = ["?", "what", "how", "why", "when", "where", "who", "is there"]
    # Discussion indicators
    discussion_signals = ["think", "opinion", "thoughts", "maybe", "perhaps",
                          "consider", "discuss", "what if"]

    command_score = sum(1 for s in command_signals if s in text_lower)
    question_score = sum(1 for s in question_signals if s in text_lower)
    discussion_score = sum(1 for s in discussion_signals if s in text_lower)

    # Boost command score if we detected actions
    command_score += len(actions) * 2

    # Determine intent
    if command_score > question_score and command_score > discussion_score:
        intent = "COMMAND"
        confidence = min(0.95, 0.6 + (command_score * 0.05))
    elif question_score > command_score:
        intent = "INFORMATION"
        confidence = min(0.90, 0.5 + (question_score * 0.1))
    elif discussion_score > 0:
        intent = "DISCUSSION"
        confidence = min(0.85, 0.5 + (discussion_score * 0.1))
    else:
        intent = "SUGGESTION"
        confidence = 0.5

    return {
        "intent": intent,
        "confidence": round(confidence, 2),
        "should_execute": intent == "COMMAND",
        "scores": {
            "command": command_score,
            "question": question_score,
            "discussion": discussion_score
        }
    }


# ──────────────────────────────────────────────
# Stage 3: Context Resolution
# ──────────────────────────────────────────────
def resolve_context(text: str) -> dict:
    """
    Stage 3: Resolve contextual references in the text.
    Converts 'tomorrow' → actual date, extracts times, people, etc.
    """
    now = datetime.now()
    resolved = {
        "times": [],
        "people": [],
        "priority": "Medium",
        "resolved_dates": {}
    }

    # Extract times
    for pattern in TIME_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        resolved["times"].extend(matches)

    # Resolve relative dates
    text_lower = text.lower()
    if "tomorrow" in text_lower:
        tomorrow = now + timedelta(days=1)
        resolved["resolved_dates"]["tomorrow"] = tomorrow.strftime("%Y-%m-%d")
    if "today" in text_lower:
        resolved["resolved_dates"]["today"] = now.strftime("%Y-%m-%d")
    if "next week" in text_lower:
        next_monday = now + timedelta(days=(7 - now.weekday()))
        resolved["resolved_dates"]["next week"] = next_monday.strftime("%Y-%m-%d")

    # Day name resolution
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in day_names:
        if day in text_lower:
            days_ahead = (day_names.index(day) - now.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            target = now + timedelta(days=days_ahead)
            resolved["resolved_dates"][day] = target.strftime("%Y-%m-%d")

    # Extract people/teams
    for pattern in PERSON_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        resolved["people"].extend(matches)

    # Determine priority
    for level, keywords in PRIORITY_MAP.items():
        if any(kw in text_lower for kw in keywords):
            resolved["priority"] = level.capitalize()
            break

    return resolved


# ──────────────────────────────────────────────
# Stage 4: RPC Planner
# ──────────────────────────────────────────────
TOOL_MAP = {
    "SCHEDULE_EVENT": "schedule_event",
    "TRIGGER_ALERT": "trigger_alert",
    "CREATE_TICKET": "create_ticket",
    "CREATE_REMINDER": "create_reminder"
}


def plan_rpcs(actions: list[dict], context: dict) -> list[dict]:
    """
    Stage 4: Map semantic actions to MCP tool function calls with parameters.
    """
    rpcs = []

    for action in actions:
        action_type = action["type"]
        tool_name = TOOL_MAP.get(action_type)
        if not tool_name:
            continue

        params = {}
        if action_type == "SCHEDULE_EVENT":
            params = {
                "topic": _extract_topic(action["raw_text"]),
                "time": context["times"][0] if context["times"] else "TBD",
                "participants": context["people"] if context["people"] else ["team"]
            }
        elif action_type == "TRIGGER_ALERT":
            params = {
                "system": _extract_system(action["raw_text"]),
                "issue": _extract_issue(action["raw_text"]),
                "priority": context["priority"]
            }
        elif action_type == "CREATE_TICKET":
            params = {
                "assignee": context["people"][0] if context["people"] else "unassigned",
                "summary": _extract_topic(action["raw_text"]),
                "due": context["times"][0] if context["times"] else "TBD",
                "priority": context["priority"]
            }
        elif action_type == "CREATE_REMINDER":
            params = {
                "message": _extract_topic(action["raw_text"]),
                "time": context["times"][0] if context["times"] else "TBD",
                "target": context["people"][0] if context["people"] else "self"
            }

        rpcs.append({
            "tool": tool_name,
            "params": params,
            "action_type": action_type
        })

    return rpcs


# ──────────────────────────────────────────────
# Text extraction helpers
# ──────────────────────────────────────────────
def _extract_topic(text: str) -> str:
    """Extract a meaningful topic/summary from the text."""
    # Remove common prefixes
    for prefix in ["hey, ", "please ", "can you ", "also "]:
        text = re.sub(f"^{prefix}", "", text, flags=re.IGNORECASE)
    # Truncate to a reasonable length
    words = text.split()
    if len(words) > 8:
        return " ".join(words[:8]) + "..."
    return text.strip()


def _extract_system(text: str) -> str:
    """Extract system/component name from alert text."""
    # Look for system-like terms
    system_patterns = [
        r'(?:the\s+)?(\w+(?:\s+\w+)?\s+(?:gateway|server|api|service|database|db|system))',
        r'(?:the\s+)?(\w+)\s+(?:is|are)\s+(?:down|failing|broken|throwing)',
    ]
    for pattern in system_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()
    return "Unknown System"


def _extract_issue(text: str) -> str:
    """Extract the issue description from alert text."""
    issue_patterns = [
        r'(?:throwing|getting|has)\s+(.+?)(?:\.|!|$)',
        r'(\d+\s+errors?)',
        r'(is\s+(?:down|failing|broken|crashed))'
    ]
    for pattern in issue_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Unknown issue"


# ──────────────────────────────────────────────
# Full Pipeline
# ──────────────────────────────────────────────
def process_message(text: str) -> dict:
    """
    Run the full semantic routing pipeline on a message.
    Returns the complete execution trace.
    """
    # Stage 1: Extract actions
    actions = extract_actions(text)

    # Stage 2: Classify intent
    intent = classify_intent(text, actions)

    # Stage 3: Resolve context
    context = resolve_context(text)

    # Stage 4: Plan RPCs
    rpcs = plan_rpcs(actions, context) if intent["should_execute"] else []

    # Governance check
    governance = {
        "confidence_threshold": 0.85,
        "confidence_met": intent["confidence"] >= 0.85,
        "intent_is_command": intent["intent"] == "COMMAND",
        "execution_approved": intent["should_execute"],
        "actions_count": len(rpcs)
    }

    return {
        "input": text,
        "pipeline": {
            "stage_1_extraction": {
                "actions_found": len(actions),
                "actions": actions
            },
            "stage_2_classification": intent,
            "stage_3_context": context,
            "stage_4_rpc_plan": rpcs,
            "governance": governance
        }
    }


# ──────────────────────────────────────────────
# CLI Demo
# ──────────────────────────────────────────────
def print_trace(result: dict) -> None:
    """Pretty-print the execution trace for demo purposes."""
    import json as _json

    print("\n" + "═" * 60)
    print("🧠 ContextOS Semantic Router - Execution Trace")
    print("═" * 60)

    print(f"\n📝 Input: \"{result['input']}\"")

    pipeline = result["pipeline"]

    # Stage 1
    print(f"\n{'─' * 40}")
    print(f"Stage 1 — Semantic Extraction")
    print(f"  Actions found: {pipeline['stage_1_extraction']['actions_found']}")
    for a in pipeline["stage_1_extraction"]["actions"]:
        print(f"  • {a['type']}: {a['description']} (keywords: {a['matched_keywords']})")

    # Stage 2
    print(f"\n{'─' * 40}")
    print(f"Stage 2 — Intent Classification")
    cls = pipeline["stage_2_classification"]
    emoji = "✅" if cls["should_execute"] else "❌"
    print(f"  Intent: {cls['intent']} | Confidence: {cls['confidence']}")
    print(f"  {emoji} Execute: {cls['should_execute']}")

    # Stage 3
    print(f"\n{'─' * 40}")
    print(f"Stage 3 — Context Resolution")
    ctx = pipeline["stage_3_context"]
    print(f"  Times: {ctx['times'] if ctx['times'] else 'none detected'}")
    print(f"  People: {ctx['people'] if ctx['people'] else 'none detected'}")
    print(f"  Priority: {ctx['priority']}")
    if ctx["resolved_dates"]:
        for label, date in ctx["resolved_dates"].items():
            print(f"  📅 '{label}' → {date}")

    # Stage 4
    print(f"\n{'─' * 40}")
    print(f"Stage 4 — RPC Plan")
    rpcs = pipeline["stage_4_rpc_plan"]
    if rpcs:
        for rpc in rpcs:
            print(f"  🔧 {rpc['tool']}()")
            for k, v in rpc["params"].items():
                print(f"     {k}: {v}")
    else:
        print("  ⏸️  No RPCs planned (intent not COMMAND or confidence too low)")

    # Governance
    print(f"\n{'─' * 40}")
    print(f"🔐 Governance Check")
    gov = pipeline["governance"]
    print(f"  Confidence threshold: {gov['confidence_threshold']}")
    print(f"  Confidence met: {'✅' if gov['confidence_met'] else '❌'}")
    print(f"  Execution approved: {'✅' if gov['execution_approved'] else '❌'}")
    print(f"  Total actions: {gov['actions_count']}")

    print("\n" + "═" * 60)


if __name__ == "__main__":
    # Demo scenarios
    demo_messages = [
        # Scenario 1: The Saturday Morning Crisis
        "The payment gateway is throwing 500 errors! Urgent! Also schedule a post-mortem for Monday 10am with backend-team.",

        # Scenario 2: Task Assignment
        "@Rahul revert the logo to green by 4 PM. Let's have standup tomorrow 10 AM.",

        # Scenario 3: Simple question (should NOT trigger execution)
        "What time is the standup meeting today?",

        # Scenario 4: Multi-action command
        "Alert the DevOps team that the API server is down. Create a ticket for @Sarah to fix the DNS issue by Friday. Remind me to follow up tomorrow morning."
    ]

    print("\n🚀 ContextOS Semantic Router Demo")
    print("=" * 60)
    print("This demo shows how natural language gets compiled")
    print("into structured RPC calls via the semantic pipeline.")
    print("=" * 60)

    for i, msg in enumerate(demo_messages, 1):
        print(f"\n\n{'▓' * 60}")
        print(f"  DEMO {i} of {len(demo_messages)}")
        print(f"{'▓' * 60}")
        result = process_message(msg)
        print_trace(result)

    print("\n\n✅ Demo complete! In production, Archestra handles this pipeline.")
    print("   Our MCP server receives the planned RPCs and executes them.")
