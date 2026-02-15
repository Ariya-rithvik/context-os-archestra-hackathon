"""
ContextOS — Live Chat Dashboard
A WhatsApp/Telegram-style interface for the MCP server.
Type natural language → Agents assemble → Tools execute → Results appear.

Usage:
    python dashboard.py
    Open http://localhost:5050 in your browser
"""

import json
import os
import re
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

# Import semantic router and multi-agent orchestrator
import sys
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from semantic_router import process_message
from multi_agent_system import AgentOrchestrator

# Dashboard orchestrator instance (for step-by-step responses)
_dashboard_orchestrator = AgentOrchestrator()

PORT = 5050

# Data directory (same as server.py)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ──────────────────────────────────────────────
# JSON Helpers
# ──────────────────────────────────────────────
def _load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_json(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _gen_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:4]}"


# ──────────────────────────────────────────────
# Tool Execution (direct JSON writes)
# ──────────────────────────────────────────────
def execute_rpc(rpc):
    """Execute a single RPC and return the result."""
    tool = rpc["tool"]
    p = rpc["params"]
    now = datetime.now().isoformat()

    if tool == "schedule_event":
        eid = _gen_id("EVT")
        entry = {"id": eid, "topic": p.get("topic",""), "time": p.get("time",""),
                 "participants": p.get("participants",[]), "created_at": now, "status": "scheduled"}
        data = _load_json("calendar.json"); data.append(entry); _save_json("calendar.json", data)
        return {"agent": "📅 Calendar Agent", "action": "schedule_event", "id": eid,
                "message": f"Meeting '{p.get('topic','')}' scheduled for {p.get('time','')} with {', '.join(p.get('participants',[]))}"}

    elif tool == "trigger_alert":
        aid = _gen_id("ALT")
        entry = {"id": aid, "system": p.get("system",""), "issue": p.get("issue",""),
                 "priority": p.get("priority","medium"), "created_at": now, "status": "active"}
        data = _load_json("alerts.json"); data.append(entry); _save_json("alerts.json", data)
        return {"agent": "🚨 Alert Agent", "action": "trigger_alert", "id": aid,
                "message": f"Alert sent for {p.get('system','')} — {p.get('issue','')} [{p.get('priority','').upper()}]"}

    elif tool == "create_ticket":
        tid = _gen_id("TKT")
        entry = {"id": tid, "assignee": p.get("assignee",""), "summary": p.get("summary",""),
                 "due": p.get("due",""), "priority": p.get("priority","medium"), "created_at": now, "status": "open"}
        data = _load_json("tickets.json"); data.append(entry); _save_json("tickets.json", data)
        return {"agent": "🎫 Ticket Agent", "action": "create_ticket", "id": tid,
                "message": f"Ticket assigned to {p.get('assignee','')}: '{p.get('summary','')}' — due {p.get('due','')}"}

    elif tool == "create_reminder":
        rid = _gen_id("REM")
        entry = {"id": rid, "message": p.get("message",""), "time": p.get("time",""),
                 "target": p.get("target",""), "created_at": now, "status": "pending"}
        data = _load_json("reminders.json"); data.append(entry); _save_json("reminders.json", data)
        return {"agent": "⏰ Reminder Agent", "action": "create_reminder", "id": rid,
                "message": f"Reminder set for {p.get('target','')}: '{p.get('message','')}' at {p.get('time','')}"}

    return {"agent": "❓ Unknown", "action": tool, "id": "", "message": "Unknown tool"}


def process_chat(text):
    """Process a chat message through the multi-agent orchestrator.
    Returns rich step-by-step response lines."""
    # Use orchestrator for rich step-by-step responses
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_dashboard_orchestrator.route_message(text))
        loop.close()
    except Exception as e:
        return {
            "input": text,
            "response_lines": [f"❌ Error: {str(e)}"],
            "tasks": [],
            "total_tasks": 0,
            "approved": False,
            "executed": [],
        }
    
    # Also run semantic router for metadata
    nlp = process_message(text)
    pipeline = nlp["pipeline"]
    
    # Build executed array for backward compat with dashboard JS
    executed = []
    for task in result.get("tasks", []):
        steps = task.get("steps", [])
        executed.append({
            "agent": task.get("agent", "Agent"),
            "action": task.get("agent", "unknown"),
            "id": task.get("result", {}).get("ticket_id", "") or task.get("result", {}).get("event_id", "") or task.get("result", {}).get("alert_id", "") or "",
            "message": "\n".join(steps) if steps else "Done",
            "steps": steps,
        })
    
    return {
        "input": text,
        "intent": pipeline["stage_2_classification"]["intent"],
        "confidence": pipeline["stage_2_classification"]["confidence"],
        "actions_found": pipeline["stage_1_extraction"]["actions_found"],
        "actions": pipeline["stage_1_extraction"]["actions"],
        "context": pipeline["stage_3_context"],
        "approved": len(executed) > 0,
        "executed": executed,
        "response_lines": result.get("response_lines", []),
        "total_tasks": result.get("total_tasks", 0),
    }


# ──────────────────────────────────────────────
# HTML — Full Chat UI
# ──────────────────────────────────────────────
APP_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ContextOS — Agents Chat</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
<style>
/* ═══════════════════════ RESET & VARS ═══════════════════════ */
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#07070d;
  --bg2:#0d0d16;
  --surface:rgba(255,255,255,0.035);
  --surface2:rgba(255,255,255,0.06);
  --surface3:rgba(255,255,255,0.09);
  --glass:rgba(16,16,28,0.65);
  --glass2:rgba(20,20,35,0.8);
  --border:rgba(255,255,255,0.06);
  --border2:rgba(255,255,255,0.1);
  --text:#e8e8f0;
  --text2:#a0a0b8;
  --text3:#6a6a82;
  --accent:#7c6aef;
  --accent2:#9d8cf8;
  --accent-glow:rgba(124,106,239,.2);
  --green:#3dd68c;
  --green-bg:rgba(61,214,140,.1);
  --red:#ef6a6a;
  --red-bg:rgba(239,106,106,.1);
  --amber:#efb83d;
  --amber-bg:rgba(239,184,61,.1);
  --blue:#6aaeef;
  --blue-bg:rgba(106,174,239,.1);
  --purple:#b06aef;
  --purple-bg:rgba(176,106,239,.1);
  --r:16px;--rs:10px;--rr:24px;
  --sidebar-w:72px;
  --shadow:0 8px 32px rgba(0,0,0,.4);
}
html{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);overflow:hidden;height:100%}
body{height:100%;display:flex;position:relative}

/* ═══════════════════════ ANIMATED BG ═══════════════════════ */
.bg-mesh{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;overflow:hidden;pointer-events:none}
.bg-mesh .orb{position:absolute;border-radius:50%;filter:blur(100px);opacity:.12;animation:orbFloat 20s ease-in-out infinite}
.bg-mesh .orb:nth-child(1){width:600px;height:600px;background:#7c6aef;top:-10%;left:-5%;animation-delay:0s}
.bg-mesh .orb:nth-child(2){width:500px;height:500px;background:#3dd68c;bottom:-15%;right:-5%;animation-delay:-7s}
.bg-mesh .orb:nth-child(3){width:400px;height:400px;background:#ef6a6a;top:50%;left:40%;animation-delay:-14s}
@keyframes orbFloat{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(40px,-30px) scale(1.1)}66%{transform:translate(-20px,40px) scale(.9)}}

/* ═══════════════════════ SIDEBAR ═══════════════════════ */
.sidebar{width:var(--sidebar-w);height:100%;background:var(--glass2);backdrop-filter:blur(30px);-webkit-backdrop-filter:blur(30px);border-right:1px solid var(--border);display:flex;flex-direction:column;align-items:center;padding:1rem 0;z-index:10;position:relative;flex-shrink:0}
.sidebar-logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#7c6aef,#5a4ad4);display:flex;align-items:center;justify-content:center;font-size:1.2rem;margin-bottom:1.5rem;box-shadow:0 0 24px var(--accent-glow);cursor:pointer;transition:transform .2s}
.sidebar-logo:hover{transform:scale(1.08)}
.nav-items{display:flex;flex-direction:column;gap:.5rem;flex:1}
.nav-btn{width:46px;height:46px;border-radius:14px;border:none;background:transparent;color:var(--text3);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;position:relative;font-family:inherit}
.nav-btn:hover{background:var(--surface2);color:var(--text2)}
.nav-btn.active{background:var(--accent-glow);color:var(--accent2)}
.nav-btn.active::before{content:'';position:absolute;left:-12px;width:3px;height:20px;border-radius:0 3px 3px 0;background:var(--accent)}
.nav-btn .material-icons-round{font-size:22px}
.nav-badge{position:absolute;top:4px;right:4px;width:8px;height:8px;border-radius:50%;background:var(--green)}

/* ═══════════════════════ MAIN CONTENT ═══════════════════════ */
.main{flex:1;display:flex;flex-direction:column;position:relative;z-index:1;height:100%;overflow:hidden}

/* ═══════════════════════ HEADER ═══════════════════════ */
.header{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 1.5rem;border-bottom:1px solid var(--border);background:var(--glass);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);flex-shrink:0}
.header-title{font-size:1.05rem;font-weight:700;display:flex;align-items:center;gap:.6rem}
.header-title .material-icons-round{font-size:20px;color:var(--accent2)}
.header-badge{display:flex;align-items:center;gap:.4rem;font-size:.72rem;font-weight:600;color:var(--green);background:var(--green-bg);border:1px solid rgba(61,214,140,.15);padding:.3rem .7rem;border-radius:100px}
.header-badge .dot{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(61,214,140,.4)}50%{opacity:.7;box-shadow:0 0 0 6px rgba(61,214,140,0)}}

/* ═══════════════════════ CHAT PAGE ═══════════════════════ */
.page{display:none;flex:1;flex-direction:column;overflow:hidden}
.page.active{display:flex}

.chat-messages{flex:1;overflow-y:auto;padding:1.5rem;display:flex;flex-direction:column;gap:1rem}
.chat-messages::-webkit-scrollbar{width:5px}
.chat-messages::-webkit-scrollbar-thumb{background:rgba(255,255,255,.08);border-radius:5px}

/* Message Bubbles */
.msg{display:flex;gap:.75rem;max-width:85%;animation:msgIn .4s cubic-bezier(.16,1,.3,1)}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.msg.system{align-self:flex-start}
@keyframes msgIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

.msg-avatar{width:36px;height:36px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0}
.msg.user .msg-avatar{background:linear-gradient(135deg,#7c6aef,#5a4ad4);box-shadow:0 4px 12px var(--accent-glow)}
.msg.system .msg-avatar{background:var(--surface2);border:1px solid var(--border)}

.msg-bubble{border-radius:var(--r);padding:.85rem 1.15rem;line-height:1.6;font-size:.88rem;position:relative}
.msg.user .msg-bubble{background:linear-gradient(135deg,rgba(124,106,239,.2),rgba(124,106,239,.08));border:1px solid rgba(124,106,239,.15);border-bottom-right-radius:4px}
.msg.system .msg-bubble{background:var(--glass);backdrop-filter:blur(12px);border:1px solid var(--border);border-bottom-left-radius:4px}
.msg-time{font-size:.65rem;color:var(--text3);margin-top:.4rem}
.msg.user .msg-time{text-align:right}

/* Agent Assembly */
.agent-assembly{margin:.5rem 0;animation:msgIn .5s cubic-bezier(.16,1,.3,1)}
.assembly-header{display:flex;align-items:center;gap:.6rem;margin-bottom:.75rem;padding:.6rem 1rem;background:linear-gradient(135deg,rgba(124,106,239,.12),rgba(61,214,140,.08));border:1px solid rgba(124,106,239,.12);border-radius:var(--r);backdrop-filter:blur(8px)}
.assembly-title{font-size:.85rem;font-weight:700;color:var(--accent2)}
.assembly-subtitle{font-size:.7rem;color:var(--text3)}
.agent-cards{display:flex;flex-direction:column;gap:.5rem}
.agent-card{display:flex;align-items:center;gap:.75rem;padding:.75rem 1rem;background:var(--glass);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:var(--rs);animation:agentIn .5s cubic-bezier(.16,1,.3,1) both}
.agent-card:nth-child(1){animation-delay:.2s}
.agent-card:nth-child(2){animation-delay:.4s}
.agent-card:nth-child(3){animation-delay:.6s}
.agent-card:nth-child(4){animation-delay:.8s}
@keyframes agentIn{from{opacity:0;transform:translateX(-20px) scale(.95)}to{opacity:1;transform:translateX(0) scale(1)}}
.agent-icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0}
.agent-icon.calendar{background:var(--blue-bg);border:1px solid rgba(106,174,239,.2)}
.agent-icon.alert{background:var(--red-bg);border:1px solid rgba(239,106,106,.2)}
.agent-icon.ticket{background:var(--amber-bg);border:1px solid rgba(239,184,61,.2)}
.agent-icon.reminder{background:var(--purple-bg);border:1px solid rgba(176,106,239,.2)}
.agent-info{flex:1}
.agent-name{font-size:.8rem;font-weight:700}
.agent-status{font-size:.72rem;color:var(--text3);margin-top:.15rem}
.agent-status.done{color:var(--green)}
.agent-badge{font-size:.65rem;font-weight:700;padding:.2rem .5rem;border-radius:6px;text-transform:uppercase;letter-spacing:.04em}
.agent-badge.done{background:var(--green-bg);color:var(--green);border:1px solid rgba(61,214,140,.2)}
.agent-badge.working{background:var(--amber-bg);color:var(--amber);border:1px solid rgba(239,184,61,.2);animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.5}}

/* Result cards */
.result-card{padding:.65rem 1rem;background:var(--surface);border:1px solid var(--border);border-radius:var(--rs);margin-top:.3rem;font-size:.78rem;color:var(--text2);display:flex;align-items:center;gap:.5rem}
.result-card .rid{font-family:monospace;font-size:.65rem;color:var(--text3);margin-left:auto}

/* ═══════════════════════ CHAT INPUT ═══════════════════════ */
.chat-input-area{padding:1rem 1.5rem;border-top:1px solid var(--border);background:var(--glass);backdrop-filter:blur(24px);flex-shrink:0}
.chat-input-wrap{display:flex;align-items:center;gap:.75rem;background:var(--surface2);border:1px solid var(--border);border-radius:var(--rr);padding:.5rem .5rem .5rem 1.25rem;transition:border-color .2s}
.chat-input-wrap:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}
.chat-input{flex:1;background:none;border:none;outline:none;color:var(--text);font-family:inherit;font-size:.9rem;line-height:1.5}
.chat-input::placeholder{color:var(--text3)}
.send-btn{width:42px;height:42px;border-radius:50%;border:none;background:linear-gradient(135deg,#7c6aef,#5a4ad4);color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0}
.send-btn:hover{transform:scale(1.06);box-shadow:0 4px 16px var(--accent-glow)}
.send-btn:active{transform:scale(.95)}
.send-btn:disabled{opacity:.4;cursor:default;transform:none}
.send-btn .material-icons-round{font-size:20px}

/* ═══════════════════════ DATA PAGES ═══════════════════════ */
.data-page-content{flex:1;overflow-y:auto;padding:1.5rem}
.data-page-content::-webkit-scrollbar{width:5px}
.data-page-content::-webkit-scrollbar-thumb{background:rgba(255,255,255,.08);border-radius:5px}

.page-hero{margin-bottom:1.5rem}
.page-hero h2{font-size:1.5rem;font-weight:800;letter-spacing:-.02em;margin-bottom:.3rem}
.page-hero p{font-size:.85rem;color:var(--text3)}

.data-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1rem}
.data-card{background:var(--glass);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:var(--r);padding:1.15rem 1.35rem;transition:all .25s ease;animation:cardIn .4s ease both}
.data-card:hover{border-color:var(--border2);transform:translateY(-2px);box-shadow:var(--shadow)}
@keyframes cardIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.data-card .card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:.6rem}
.data-card .card-title{font-size:.92rem;font-weight:700}
.data-card .card-meta{font-size:.72rem;color:var(--text3);line-height:1.5}
.data-card .card-id{font-family:monospace;font-size:.65rem;color:var(--text3);margin-top:.5rem}
.priority-tag{font-size:.6rem;font-weight:700;padding:.2rem .5rem;border-radius:6px;text-transform:uppercase;letter-spacing:.04em}
.priority-tag.high{background:var(--red-bg);color:var(--red);border:1px solid rgba(239,106,106,.2)}
.priority-tag.medium{background:var(--amber-bg);color:var(--amber);border:1px solid rgba(239,184,61,.2)}
.priority-tag.low{background:var(--green-bg);color:var(--green);border:1px solid rgba(61,214,140,.2)}
.status-tag{font-size:.6rem;font-weight:700;padding:.2rem .5rem;border-radius:6px;text-transform:uppercase;letter-spacing:.04em}
.status-tag.scheduled{background:var(--blue-bg);color:var(--blue);border:1px solid rgba(106,174,239,.2)}
.status-tag.active{background:var(--red-bg);color:var(--red);border:1px solid rgba(239,106,106,.2)}
.status-tag.open{background:var(--amber-bg);color:var(--amber);border:1px solid rgba(239,184,61,.2)}
.status-tag.pending{background:var(--purple-bg);color:var(--purple);border:1px solid rgba(176,106,239,.2)}

.empty-state{text-align:center;padding:4rem 2rem;color:var(--text3)}
.empty-state .empty-icon{font-size:3rem;margin-bottom:1rem;opacity:.4}
.empty-state p{font-size:.9rem;line-height:1.6}

/* ═══════════════════════ STATS BAR ═══════════════════════ */
.stats-bar{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem;margin-bottom:1.5rem}
.stat-mini{background:var(--glass);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:var(--rs);padding:.85rem 1rem;display:flex;align-items:center;gap:.75rem;transition:all .2s}
.stat-mini:hover{border-color:var(--border2);background:var(--surface2)}
.stat-mini .stat-icon{font-size:1.3rem}
.stat-mini .stat-num{font-size:1.4rem;font-weight:800;letter-spacing:-.02em}
.stat-mini .stat-lbl{font-size:.65rem;color:var(--text3);text-transform:uppercase;letter-spacing:.04em}

/* ═══════════════════════ WELCOME ═══════════════════════ */
.welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:3rem;text-align:center;flex:1}
.welcome-icon{font-size:4rem;margin-bottom:1.5rem;animation:float 3s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.welcome h2{font-size:1.8rem;font-weight:800;letter-spacing:-.03em;margin-bottom:.5rem;background:linear-gradient(135deg,var(--accent2),var(--green));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.welcome p{color:var(--text3);font-size:.9rem;line-height:1.6;max-width:450px}
.welcome-examples{margin-top:2rem;display:flex;flex-direction:column;gap:.5rem;width:100%;max-width:500px}
.example-chip{text-align:left;padding:.75rem 1rem;background:var(--surface);border:1px solid var(--border);border-radius:var(--rs);font-size:.82rem;color:var(--text2);cursor:pointer;transition:all .2s;font-family:inherit}
.example-chip:hover{background:var(--surface2);border-color:var(--accent);color:var(--text);transform:translateX(4px)}
.example-chip span{color:var(--text3);font-size:.7rem}
</style>
</head>
<body>

<!-- Animated Background -->
<div class="bg-mesh">
  <div class="orb"></div>
  <div class="orb"></div>
  <div class="orb"></div>
</div>

<!-- Sidebar -->
<aside class="sidebar">
  <div class="sidebar-logo" title="ContextOS">⚡</div>
  <div class="nav-items">
    <button class="nav-btn active" data-page="chat" title="Chat">
      <span class="material-icons-round">chat_bubble</span>
      <span class="nav-badge" style="display:none"></span>
    </button>
    <button class="nav-btn" data-page="calendar" title="Calendar">
      <span class="material-icons-round">event</span>
    </button>
    <button class="nav-btn" data-page="alerts" title="Alerts">
      <span class="material-icons-round">notifications_active</span>
    </button>
    <button class="nav-btn" data-page="tickets" title="Tickets">
      <span class="material-icons-round">confirmation_number</span>
    </button>
    <button class="nav-btn" data-page="reminders" title="Reminders">
      <span class="material-icons-round">alarm</span>
    </button>
  </div>
</aside>

<!-- Main Content -->
<div class="main">

  <!-- Header -->
  <div class="header">
    <div class="header-title" id="header-title">
      <span class="material-icons-round">smart_toy</span>
      ContextOS Agents
    </div>
    <div class="header-badge"><span class="dot"></span> LIVE</div>
  </div>

  <!-- 💬 CHAT PAGE -->
  <div class="page active" id="page-chat">
    <div class="chat-messages" id="chat-messages">
      <div class="welcome" id="welcome">
        <div class="welcome-icon">🦸‍♂️</div>
        <h2>Agents, Assemble!</h2>
        <p>Type a natural language command below and watch the agents come to life. They'll analyze your message and execute real actions.</p>
        <div class="welcome-examples">
          <button class="example-chip" onclick="useExample(this)" data-msg="Schedule a standup for Monday 10am with Alice and Bob">
            📅 "Schedule a standup for Monday 10am with Alice and Bob" <span>→ Calendar Agent</span>
          </button>
          <button class="example-chip" onclick="useExample(this)" data-msg="The payment gateway is throwing 500 errors! Alert the backend-team immediately">
            🚨 "Payment gateway is throwing 500 errors! Alert backend-team" <span>→ Alert Agent</span>
          </button>
          <button class="example-chip" onclick="useExample(this)" data-msg="Assign a ticket to Dana to fix the login bug by Friday, high priority">
            🎫 "Assign a ticket to Dana to fix the login bug by Friday" <span>→ Ticket Agent</span>
          </button>
          <button class="example-chip" onclick="useExample(this)" data-msg="Remind the product team to follow up on the design mockups tomorrow morning">
            ⏰ "Remind product team to follow up on design mockups" <span>→ Reminder Agent</span>
          </button>
        </div>
      </div>
    </div>
    <div class="chat-input-area">
      <div class="chat-input-wrap">
        <input type="text" class="chat-input" id="chat-input" placeholder="Type a command... e.g. 'Schedule a meeting with the team'" autocomplete="off">
        <button class="send-btn" id="send-btn" onclick="sendMessage()">
          <span class="material-icons-round">send</span>
        </button>
      </div>
    </div>
  </div>

  <!-- 📅 CALENDAR PAGE -->
  <div class="page" id="page-calendar">
    <div class="data-page-content">
      <div class="page-hero"><h2>📅 Calendar</h2><p>All scheduled meetings and events</p></div>
      <div class="stats-bar" id="cal-stats"></div>
      <div class="data-grid" id="calendar-grid"></div>
    </div>
  </div>

  <!-- 🚨 ALERTS PAGE -->
  <div class="page" id="page-alerts">
    <div class="data-page-content">
      <div class="page-hero"><h2>🚨 Alerts</h2><p>Active system alerts and incidents</p></div>
      <div class="stats-bar" id="alert-stats"></div>
      <div class="data-grid" id="alerts-grid"></div>
    </div>
  </div>

  <!-- 🎫 TICKETS PAGE -->
  <div class="page" id="page-tickets">
    <div class="data-page-content">
      <div class="page-hero"><h2>🎫 Tickets</h2><p>Open tasks and assignments</p></div>
      <div class="stats-bar" id="ticket-stats"></div>
      <div class="data-grid" id="tickets-grid"></div>
    </div>
  </div>

  <!-- ⏰ REMINDERS PAGE -->
  <div class="page" id="page-reminders">
    <div class="data-page-content">
      <div class="page-hero"><h2>⏰ Reminders</h2><p>Pending follow-ups and notifications</p></div>
      <div class="stats-bar" id="rem-stats"></div>
      <div class="data-grid" id="reminders-grid"></div>
    </div>
  </div>

</div>

<script>
/* ═══════════════════════ NAVIGATION ═══════════════════════ */
const pages = {chat:'ContextOS Agents',calendar:'Calendar',alerts:'Alerts',tickets:'Tickets',reminders:'Reminders'};
const icons = {chat:'smart_toy',calendar:'event',alerts:'notifications_active',tickets:'confirmation_number',reminders:'alarm'};
let currentPage = 'chat';

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const page = btn.dataset.page;
    switchPage(page);
  });
});

function switchPage(page) {
  currentPage = page;
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelector(`[data-page="${page}"]`).classList.add('active');
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  document.getElementById('header-title').innerHTML = `<span class="material-icons-round">${icons[page]}</span> ${pages[page]}`;
  if (page !== 'chat') loadDataPage(page);
}

/* ═══════════════════════ CHAT ═══════════════════════ */
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
let hasMessages = false;

chatInput.addEventListener('keydown', e => {if(e.key==='Enter'&&!e.shiftKey)sendMessage()});

function useExample(el) {
  chatInput.value = el.dataset.msg;
  chatInput.focus();
}

function timeNow() {
  return new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}

function addMsg(type, html, extra='') {
  if (!hasMessages) {
    const w = document.getElementById('welcome');
    if (w) w.style.display = 'none';
    hasMessages = true;
  }
  const avatar = type === 'user' ? '👤' : '⚡';
  const div = document.createElement('div');
  div.className = 'msg ' + type;
  div.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div>
      <div class="msg-bubble">${html}</div>
      ${extra}
      <div class="msg-time">${timeNow()}</div>
    </div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;
  chatInput.value = '';
  sendBtn.disabled = true;

  // User bubble
  addMsg('user', text);

  // Thinking indicator
  const thinking = document.createElement('div');
  thinking.className = 'agent-assembly';
  thinking.innerHTML = `
    <div class="assembly-header">
      <div>
        <div class="assembly-title">🧠 Analyzing message...</div>
        <div class="assembly-subtitle">Running semantic pipeline</div>
      </div>
    </div>`;
  chatMessages.appendChild(thinking);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();

    // Remove thinking
    thinking.remove();

    if (!data.approved || !data.executed || data.executed.length === 0) {
      addMsg('system', `I understood your message but couldn't identify a clear action to execute.<br><br><span style="color:var(--text3);font-size:.78rem">Intent: ${data.intent} • Confidence: ${(data.confidence*100).toFixed(0)}% • Actions found: ${data.actions_found}</span><br><span style="color:var(--text3);font-size:.78rem">Try being more specific, like "Schedule a meeting..." or "Alert the team about..."</span>`);
    } else {
      // AGENTS ASSEMBLE with step-by-step traces!
      const assembly = document.createElement('div');
      assembly.className = 'agent-assembly';

      const agentIcons = {
        'CalendarAgent': {icon:'📅', cls:'calendar', name:'Calendar Agent'},
        'AlertAgent': {icon:'🚨', cls:'alert', name:'Alert Agent'},
        'TaskAgent': {icon:'🎫', cls:'ticket', name:'Task Agent'},
        'SearchAgent': {icon:'🔍', cls:'calendar', name:'Search Agent'},
        'MessageDeliveryAgent': {icon:'📨', cls:'reminder', name:'Message Delivery Agent'},
        'DelegationAgent': {icon:'👤', cls:'calendar', name:'Delegation Agent'},
      };

      let cardsHtml = '';
      data.executed.forEach((ex, i) => {
        const ai = agentIcons[ex.agent] || {icon:'🤖', cls:'calendar', name: ex.agent || 'Agent'};
        const steps = ex.steps || [ex.message || 'Done'];
        const stepsHtml = steps.filter(s => s).map(s => `<div class="agent-step">${s}</div>`).join('');
        cardsHtml += `
          <div class="agent-card" style="animation-delay:${0.2 + i*0.2}s">
            <div class="agent-icon ${ai.cls}">${ai.icon}</div>
            <div class="agent-info">
              <div class="agent-name">${ai.name}</div>
              <div class="agent-status done" style="white-space:pre-line">${stepsHtml}</div>
            </div>
            <span class="agent-badge done">Done</span>
          </div>`;
      });

      assembly.innerHTML = `
        <div class="assembly-header">
          <div>
            <div class="assembly-title">🦸 Agents Assembled!</div>
            <div class="assembly-subtitle">${data.executed.length} agent${data.executed.length>1?'s':''} deployed • Intent: ${data.intent} • Confidence: ${(data.confidence*100).toFixed(0)}%</div>
          </div>
        </div>
        <div class="agent-cards">${cardsHtml}</div>`;

      chatMessages.appendChild(assembly);

      // Step-by-step summary response
      const lines = (data.response_lines || []).filter(l => l).map(l => l).join('<br>');
      setTimeout(() => {
        addMsg('system', `<strong>⚡ All done!</strong><br><br>${lines}<br><br><span style="color:var(--text3);font-size:.75rem">📁 Data saved to JSON proof files</span>`);
      }, 600 + data.executed.length * 200);
    }
  } catch(e) {
    thinking.remove();
    addMsg('system', `<span style="color:var(--red)">Error: ${e.message}</span>`);
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
    setTimeout(() => chatMessages.scrollTop = chatMessages.scrollHeight, 800);
  }
}

/* ═══════════════════════ DATA PAGES ═══════════════════════ */
async function loadDataPage(page) {
  try {
    const res = await fetch('/api/activity');
    const d = await res.json();

    if (page === 'calendar') renderCalendar(d.meetings);
    else if (page === 'alerts') renderAlerts(d.alerts);
    else if (page === 'tickets') renderTickets(d.tickets);
    else if (page === 'reminders') renderReminders(d.reminders);
  } catch(e) { console.error(e); }
}

function timeAgo(iso) {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff/60) + 'm ago';
  if (diff < 86400) return Math.floor(diff/3600) + 'h ago';
  return Math.floor(diff/86400) + 'd ago';
}

function renderCalendar(items) {
  const grid = document.getElementById('calendar-grid');
  const stats = document.getElementById('cal-stats');
  stats.innerHTML = `<div class="stat-mini"><span class="stat-icon">📅</span><div><div class="stat-num">${items.length}</div><div class="stat-lbl">Total Events</div></div></div>`;
  if (!items.length) { grid.innerHTML = '<div class="empty-state"><div class="empty-icon">📅</div><p>No meetings scheduled yet.<br>Try: "Schedule a standup for Monday 10am with Alice"</p></div>'; return; }
  grid.innerHTML = items.slice().reverse().map((e,i) => `
    <div class="data-card" style="animation-delay:${i*0.05}s">
      <div class="card-header">
        <div class="card-title">📅 ${e.topic}</div>
        <span class="status-tag scheduled">${e.status}</span>
      </div>
      <div class="card-meta">
        ⏰ ${e.time}<br>
        👥 ${(e.participants||[]).join(', ')}<br>
        🕐 ${timeAgo(e.created_at)}
      </div>
      <div class="card-id">${e.id}</div>
    </div>`).join('');
}

function renderAlerts(items) {
  const grid = document.getElementById('alerts-grid');
  const stats = document.getElementById('alert-stats');
  const high = items.filter(a => (a.priority||'').toLowerCase()==='high').length;
  stats.innerHTML = `
    <div class="stat-mini"><span class="stat-icon">🚨</span><div><div class="stat-num">${items.length}</div><div class="stat-lbl">Total Alerts</div></div></div>
    <div class="stat-mini"><span class="stat-icon">🔴</span><div><div class="stat-num">${high}</div><div class="stat-lbl">High Priority</div></div></div>`;
  if (!items.length) { grid.innerHTML = '<div class="empty-state"><div class="empty-icon">🚨</div><p>No alerts yet.<br>Try: "The payment gateway is down! Alert backend-team"</p></div>'; return; }
  grid.innerHTML = items.slice().reverse().map((e,i) => `
    <div class="data-card" style="animation-delay:${i*0.05}s">
      <div class="card-header">
        <div class="card-title">🚨 ${e.system}</div>
        <span class="priority-tag ${(e.priority||'').toLowerCase()}">${e.priority}</span>
      </div>
      <div class="card-meta">
        ⚠️ ${e.issue}<br>
        🕐 ${timeAgo(e.created_at)}
      </div>
      <div class="card-id">${e.id}</div>
    </div>`).join('');
}

function renderTickets(items) {
  const grid = document.getElementById('tickets-grid');
  const stats = document.getElementById('ticket-stats');
  stats.innerHTML = `<div class="stat-mini"><span class="stat-icon">🎫</span><div><div class="stat-num">${items.length}</div><div class="stat-lbl">Total Tickets</div></div></div>`;
  if (!items.length) { grid.innerHTML = '<div class="empty-state"><div class="empty-icon">🎫</div><p>No tickets created yet.<br>Try: "Assign a task to Dana to fix the login bug by Friday"</p></div>'; return; }
  grid.innerHTML = items.slice().reverse().map((e,i) => `
    <div class="data-card" style="animation-delay:${i*0.05}s">
      <div class="card-header">
        <div class="card-title">🎫 ${e.summary}</div>
        <span class="priority-tag ${(e.priority||'').toLowerCase()}">${e.priority}</span>
      </div>
      <div class="card-meta">
        👤 ${e.assignee}<br>
        📆 Due: ${e.due}<br>
        🕐 ${timeAgo(e.created_at)}
      </div>
      <div class="card-id">${e.id}</div>
    </div>`).join('');
}

function renderReminders(items) {
  const grid = document.getElementById('reminders-grid');
  const stats = document.getElementById('rem-stats');
  stats.innerHTML = `<div class="stat-mini"><span class="stat-icon">⏰</span><div><div class="stat-num">${items.length}</div><div class="stat-lbl">Total Reminders</div></div></div>`;
  if (!items.length) { grid.innerHTML = '<div class="empty-state"><div class="empty-icon">⏰</div><p>No reminders set yet.<br>Try: "Remind the product team about design review tomorrow"</p></div>'; return; }
  grid.innerHTML = items.slice().reverse().map((e,i) => `
    <div class="data-card" style="animation-delay:${i*0.05}s">
      <div class="card-header">
        <div class="card-title">⏰ ${e.message}</div>
        <span class="status-tag pending">${e.status}</span>
      </div>
      <div class="card-meta">
        👤 ${e.target}<br>
        🕐 ${e.time}<br>
        📌 ${timeAgo(e.created_at)}
      </div>
      <div class="card-id">${e.id}</div>
    </div>`).join('');
}
</script>
</body>
</html>"""


# ──────────────────────────────────────────────
# HTTP Handler
# ──────────────────────────────────────────────
class DashboardHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"  [Dashboard] {args[0]}")

    def _send(self, body_bytes, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body_bytes)

    def _json(self, data, status=200):
        self._send(json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json", status)

    def _html(self, html):
        self._send(html.encode("utf-8"), "text/html; charset=utf-8")

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length > 0 else b""

    # GET
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/calendar", "/alerts", "/tickets", "/reminders"):
            self._html(APP_HTML)
        elif path == "/api/activity":
            self._json({
                "meetings": _load_json("calendar.json"),
                "alerts": _load_json("alerts.json"),
                "tickets": _load_json("tickets.json"),
                "reminders": _load_json("reminders.json"),
            })
        else:
            self.send_error(404)

    # POST
    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_body()

        try:
            if path == "/api/chat":
                data = json.loads(body) if body else {}
                msg = data.get("message", "").strip()
                if not msg:
                    self._json({"error": "No message provided"}, 400)
                    return
                print(f"\n  💬 Chat: \"{msg}\"")
                result = process_chat(msg)
                for ex in result["executed"]:
                    print(f"  ✅ {ex['agent']}: {ex['message']}")
                self._json(result)
            else:
                self.send_error(404)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback; traceback.print_exc()
            self._json({"error": str(e)}, 500)

    # OPTIONS
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Connection", "close")
        self.end_headers()


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), DashboardHandler)
    print()
    print("═" * 52)
    print("  ⚡ ContextOS — Agents Chat Dashboard")
    print("═" * 52)
    print(f"  🌐  Dashboard:   http://localhost:{PORT}")
    print(f"  📡  MCP Server:  http://localhost:8000/sse")
    print(f"  📂  Data:        {DATA_DIR}")
    print("═" * 52)
    print("  Type natural language in the chat to trigger agents!")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
        server.server_close()
