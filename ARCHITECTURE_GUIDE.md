🏗️ CONTEXTOB ARCHITECTURE GUIDE
═════════════════════════════════════════════════════════════════

This explains how all the pieces fit together.


3-LAYER ARCHITECTURE
─────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: THE INPUT                                          │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│  User Types Natural Language:                              │
│  "Schedule a meeting for Monday 10am with Alice"           │
│                                                             │
│  Two Paths:                                                │
│  • Dashboard: http://localhost:5050 (testing)              │
│  • Archestra: http://localhost:3000 (production)           │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP/SSE
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ LAYER 2: THE BRAIN (Your Choice)                           │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│  Option A: Dashboard's Semantic Router (Built-in)          │
│  ├─ Stage 1: Extract Actions (keyword matching)            │
│  ├─ Stage 2: Classify Intent (COMMAND/QUESTION)            │
│  ├─ Stage 3: Resolve Context (times, people, priority)     │
│  └─ Stage 4: Plan RPCs (schedule_event, trigger_alert...)  │
│                                                             │
│  Option B: Archestra's LLM (Production)                    │
│  ├─ Uses Cerebras, OpenAI, or other LLM                    │
│  ├─ Does intent parsing on Archestra side                  │
│  └─ Calls MCP tools directly                               │
│                                                             │
│  Result: RPC call plan                                     │
│  "Call schedule_event(topic='meeting',                      │
│    time='Monday 10am', participants=['Alice'])"            │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ RPC Call (JSON)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ LAYER 3: THE HANDS (Your MCP Server)                       │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│  MCP Tools (all in Python):                                │
│                                                             │
│  schedule_event()        │  create_ticket()                │
│  ✓ topic                 │  ✓ assignee                     │
│  ✓ time                  │  ✓ summary                      │
│  ✓ participants          │  ✓ due                          │
│  ↓ saves to JSON         │  ✓ priority                     │
│                          │  ↓ saves to JSON                │
│                                                             │
│  trigger_alert()         │  create_reminder()              │
│  ✓ system                │  ✓ message                      │
│  ✓ issue                 │  ✓ time                         │
│  ✓ priority              │  ✓ target                       │
│  ↓ saves to JSON         │  ↓ saves to JSON                │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ JSON Write
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ DATA LAYER: IMMUTABLE JSON AUDIT TRAIL                     │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│  data/calendar.json      data/alerts.json                  │
│  ├─ id: EVT-a3b8         ├─ id: ALT-f177                  │
│  ├─ topic: meeting       ├─ system: Payment API           │
│  ├─ time: Monday 10am    ├─ issue: 500 errors             │
│  ├─ participants: [...]  ├─ priority: High                │
│  └─ ... (all metdata)    └─ ... (all metadata)             │
│                                                             │
│  data/tickets.json       data/reminders.json              │
│  ├─ id: TKT-18e8         ├─ id: REM-69d3                 │
│  ├─ assignee: Dana       ├─ message: review mockups       │
│  ├─ summary: Fix login   ├─ time: tomorrow 9am            │
│  ├─ due: Friday          ├─ target: product-team          │
│  └─ ... (all metadata)   └─ ... (all metadata)             │
│                                                             │
│  All entries are:                                          │
│  ✓ Human-readable (JSON)                                   │
│  ✓ Timestamped (ISO 8601)                                  │
│  ✓ Immutable (append-only)                                 │
│  ✓ Proof of execution (judges can verify)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘


DATAFLOW DIAGRAM
─────────────────────────────────────────────────────────────────

User Input
   │
   ├─ [Dashboard Path]
   │  │
   │  ├─ dashboard.py receives chat message
   │  │
   │  ├─ calls semantic_router.process_message()
   │  │   ├─ Extract actions from keywords
   │  │   ├─ Classify intent (COMMAND or others)
   │  │   ├─ Resolve context (times, people, priority)
   │  │   └─ Plan RPC calls
   │  │
   │  ├─ If approved (COMMAND + confidence 85%+):
   │  │  │
   │  │  └─ Call execute_rpc() for each planned RPC
   │  │      ├─ schedule_event()
   │  │      ├─ trigger_alert()
   │  │      ├─ create_ticket()
   │  │      └─ create_reminder()
   │  │
   │  └─ Tools write to data/*.json files
   │
   └─ [Archestra Path]
      │
      ├─ Archestra LLM processes message
      │
      ├─ Calls MCP Server at http://host.docker.internal:8000/sse
      │
      ├─ MCP Server invokes correct tool
      │  ├─ schedule_event()
      │  ├─ trigger_alert()
      │  ├─ create_ticket()
      │  └─ create_reminder()
      │
      └─ Tools write to data/*.json files


CONTROL FLOW: Message Processing
─────────────────────────────────────────────────────────────────

INPUT: "Schedule a meeting for Monday with Alice"
   │
   ├─ STAGE 1: SEMANTIC EXTRACTION
   │  ├─ Search for keywords: "meeting" ✓, "schedule" ✓
   │  ├─ Found action type: SCHEDULE_EVENT
   │  └─ matched_keywords: ["meeting", "schedule"]
   │
   ├─ STAGE 2: INTENT CLASSIFICATION
   │  ├─ Score command signals: "schedule" (1), "meeting" (1)
   │  ├─ Total score: 2 × 1 (action boost) = 2+2 = 4
   │  ├─ Confidence: min(0.95, 0.6 + 4×0.05) = 0.80
   │  ├─ Classification: COMMAND
   │  └─ Approved: Yes (COMMAND intent detected)
   │
   ├─ STAGE 3: CONTEXT RESOLUTION
   │  ├─ Extract times: ["Monday", "10am"] (if present)
   │  ├─ Extract people: ["Alice"] (named entity)
   │  ├─ Determine priority: "Medium" (default)
   │  └─ Resolve dates: "Monday" → [date object]
   │
   ├─ STAGE 4: RPC PLANNER
   │  ├─ Map action to tool: SCHEDULE_EVENT → schedule_event
   │  ├─ Fill parameters:
   │  │  ├─ topic: "schedule a meeting"
   │  │  ├─ time: "Monday" (or "10am" if extracted)
   │  │  └─ participants: ["Alice"]
   │  └─ RPC Plan: [schedule_event(topic, time, participants)]
   │
   ├─ GOVERNANCE CHECK
   │  ├─ Confidence threshold: 0.85
   │  ├─ Actual confidence: 0.80
   │  ├─ Check: 0.80 >= 0.85? NO
   │  └─ Execution approved: NO (confidence too low)
   │
   └─ OUTPUT: Not executed (confidence below threshold)
      BUT in Archestra, it would execute (Archestra does its own classification)


WHEN YOU SEND A MESSAGE IN DASHBOARD
─────────────────────────────────────────────────────────────────

1. Message sent to: POST /api/chat
   {"message": "Schedule a meeting for Monday 10am with Alice"}

2. dashboard.py does:
   ├─ Calls semantic_router.process_message(message)
   ├─ Gets full pipeline result with RPC plan
   ├─ If execution approved:
   │  ├─ Loops through planned RPCs
   │  └─ Calls execute_rpc() for each
   └─ Returns result as JSON

3. execute_rpc() function:
   ├─ Checks tool name (schedule_event)
   ├─ Extracts parameters (p = rpc["params"])
   ├─ Creates entry dict with:
   │  ├─ id: _gen_id("EVT") → EVT-a3b8
   │  ├─ topic, time, participants
   │  ├─ created_at: datetime.now()
   │  └─ status: "scheduled"
   ├─ Loads existing calendar.json
   ├─ Appends new entry
   ├─ Saves back to calendar.json
   └─ Returns success message

4. Frontend receives response:
   ├─ Displays agent assembly animation
   ├─ Shows "Calendar Agent: Meeting scheduled"
   ├─ Shows ID: EVT-a3b8
   └─ Updates calendar.json in real-time

5. Judges can verify:
   ├─ Check console logs: [MCP LOG] 📅 ACTION: Scheduling...
   ├─ Check data/calendar.json file
   └─ See timestamp and ID proving execution


WHEN CALLED VIA ARCHESTRA
─────────────────────────────────────────────────────────────────

1. User types in Archestra Chat:
   "Schedule a meeting for Monday 10am with Alice"

2. Archestra LLM processes:
   ├─ Parses intent using its own language model
   ├─ Identifies correct action: schedule_event
   ├─ Extracts parameters from context
   └─ Decides to call MCP tool

3. Archestra calls MCP Server:
   POST /rpc
   {
     "method": "schedule_event",
     "params": {
       "topic": "meeting",
       "time": "Monday 10am",
       "participants": ["Alice"]
     }
   }

4. MCP Server (server.py):
   ├─ Routes to @mcp.tool() schedule_event()
   ├─ Executes the function
   ├─ Writes to data/calendar.json
   └─ Returns result

5. Archestra receives response:
   ├─ Shows in chat: "Meeting scheduled!"
   ├─ Displays result details
   └─ Transaction complete

6. Proof available:
   ├─ data/calendar.json has new entry
   ├─ Console logs show execution
   └─ Judges can verify JSON file


FILE RELATIONSHIPS
─────────────────────────────────────────────────────────────────

server.py (MCP Server)
   ├─ Imports: fastmcp, json, os, uuid, datetime
   ├─ Defines mcp = FastMCP("ContextOS")
   ├─ Defines 4 tools with @mcp.tool() decorator
   ├─ Each tool creates/updates data/*.json
   └─ Runs on port 8000 with SSE transport

semantic_router.py (NLP Pipeline)
   ├─ Imported by: dashboard.py
   ├─ Defines: process_message(text) → full pipeline
   ├─ Stages: Extract → Classify → Resolve → Plan
   ├─ Output: RPC plan ready for execution
   └─ Can run standalone: python semantic_router.py

dashboard.py (Chat UI)
   ├─ Imports: semantic_router, json, http.server
   ├─ Defines: process_chat() → calls semantic_router
   ├─ Serves: HTML/CSS/JavaScript UI
   ├─ Endpoint: /api/chat (POST) → processes messages
   └─ Endpoint: /api/activity (GET) → returns data/*.json content

requirements.txt (Dependencies)
   ├─ fastmcp (MCP framework)
   ├─ uvicorn (ASGI server)
   ├─ fastapi (Web framework)
   ├─ pydantic (Validation)
   └─ requests (HTTP client)

data/ (Immutable Proof)
   ├─ calendar.json (events from schedule_event)
   ├─ alerts.json (entries from trigger_alert)
   ├─ tickets.json (entries from create_ticket)
   └─ reminders.json (entries from create_reminder)


EXECUTION PROOF SYSTEM
─────────────────────────────────────────────────────────────────

Why JSON files are your proof:

1. IMMUTABLE: Entries are appended, never deleted
   ✓ Shows full audit trail
   ✓ Proves each tool was called
   ✓ Shows exact parameters

2. TIMESTAMPED: Each entry has created_at
   ✓ Proves when tool was executed
   ✓ Sequence is verifiable
   ✓ No back-dating possible

3. UNIQUE IDs: EVT-a3b8, ALT-f177, etc.
   ✓ Each entry is addressable
   ✓ No duplicates
   ✓ Traceable

4. READABLE: Human-readable JSON
   ✓ Judges can see exact data
   ✓ No black-box encoding
   ✓ Fully transparent

Example judges' verification flow:
   1. Start your system
   2. Send test message: "Alert the DevOps team, issue is critical!"
   3. Check console: See [MCP LOG] 🚨 ACTION...
   4. Check data/alerts.json: See new entry with ID ALT-xxxx
   5. Proof complete! Tool executed ✓


SECURITY & ISOLATION
─────────────────────────────────────────────────────────────────

Data is isolated per file type:
   ├─ Calendar events: Only in calendar.json
   ├─ Alerts: Only in alerts.json
   ├─ Tickets: Only in tickets.json
   └─ Reminders: Only in reminders.json

No cross-contamination:
   ✓ Tool can only write to its own file
   ✓ Each tool has limited scope
   ✓ No data leakage between tools

Error isolation:
   ✓ One tool failing doesn't affect others
   ✓ Startup errors don't corrupt data
   ✓ JSON files are append-only (safe)


═════════════════════════════════════════════════════════════════

This architecture is simple, clean, and fully auditable.
Perfect for a hackathon demo!
