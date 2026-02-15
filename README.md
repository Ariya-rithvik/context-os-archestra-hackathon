# ContextOS (Archestra Hackathon Edition 🏆)


**ContextOS** is a Voice-First AI Operating System that connects your spoken intent to your digital tools. Built for the Archestra "Hack All February" event, it demonstrates a Hybrid Edge/Cloud architecture where a centralized brain orchestrates complex workflows from simple voice commands.

![Project Banner](https://via.placeholder.com/1200x300?text=ContextOS+Voice+AI+Operating+System)

## 🚀 Key Features

*   **🗣️ Voice-First Interface:** Interact naturally via Telegram voice notes (powered by `edge-tts` and `SpeechRecognition`).
*   **🧠 MCP-Based Architecture:** A custom **Model Context Protocol (MCP)** server ([server.py](cci:7://file:///d:/context-bridge/server.py:0:0-0:0)) acts as the centralized brain, exposing standardized tools to any LLM.
*   **⚡ Real-Time Dashboard:** Watch agents think, plan, and execute tasks live via a glassmorphism UI.
*   **🤖 Multi-Agent System:** Specialized agents for Calendar, Email, and DevOps alerts working in harmony.
*   **🔗 Smart Integrations:** Auto-generates Google Meet & Zoom links for meetings.

---

## 🛠️ Tech Stack

*   **Core:** Python 3.11+, `fastmcp`, `asyncio`
*   **AI Models:** Google Gemini 1.5 Flash (via API)
*   **Interface:** Telegram Bot API
*   **Voice Stack:** `SpeechRecognition` (STT), `edge-tts` (TTS)
*   **Data:** JSON-based state management (`data/*.json`)

---

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Ariya-rithvik/context-os-archestra-hackathon.git](https://github.com/Ariya-rithvik/context-os-archestra-hackathon.git)
    cd context-os-archestra-hackathon
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensures you have `fastmcp`, `python-telegram-bot`, `google-generativeai`, `edge-tts`, etc.)*

3.  **System Requirements:**
    *   **FFmpeg:** Required for voice processing. Ensure `ffmpeg` is in your system PATH.
        *   *Windows:* `winget install ffmpeg`
        *   *Mac:* `brew install ffmpeg`
        *   *Linux:* `sudo apt install ffmpeg`

---

## ⚙️ Configuration

1.  **Create your secrets file:**
    Copy `.env.example` to [.env](cci:7://file:///d:/context-bridge/.env:0:0-0:0) (if provided) or create a new `.env` file.

    ```

---
<img width="1457" height="699" alt="image" src="https://github.com/user-attachments/assets/ed59be3f-862d-4492-b919-9cd95cfda836" />


## 🏃‍♂️ How to Run

### 1. The Voice Agent (Telegram) 🎙️
This is the main "Edge Mode" demo.
```bash
python telegram_bot.py


Usage: Send a voice note or text to your bot.
Try saying: "Schedule a meeting with the design team for 5pm."
Result: The bot replies with audio and creates an event in 
data/calendar.json
.
2. The MCP Server (Archestra Mode) 🧠
Run this to expose your tools to the Archestra Gateway.

bash
python server.py
Endpoint: Connect Archestra to http://localhost:8000/sse
Tools Exposed: 
schedule_event
, trigger_alert, 
create_ticket
.
Verify: Check the logs or the Dashboard to see tools being called.
3. The Real-Time Dashboard 📊
Visualize the system's thinking process.

bash
python dashboard.py
View: Open http://localhost:5000 in your browser.
Action: Watch cards appear instantly as you interact with the bot.
🧪 Demo Scenarios
Scenario	Action (Voice/Text)	Expected Outcome
Normal Booking	"Book a table for 2 at 7pm."	Bot confirms via Audio + JSON updated.
Conflict Handling	"Actually, make a booking for 7pm for John."	Bot warns: "Conflict detected! Prioritize?"
Smart Links	"Schedule a Google Meet at 10am."	Bot generates: https://meet.google.com/...
DevOps Alert	"Payment gateway is down! Trigger alert."	System logs HIGH PRIORITY alert to alerts.json.
📂 Project Structure
context-os-archestra-hackathon/
├── data/                   # JSON state files (calendar, alerts, tickets)
├── server.py               # MCP Server (The Brain)
├── telegram_bot.py         # Voice Interface (The Ears)
├── multi_agent_system.py   # Legacy Logic (The Hands)
├── dashboard.py            # Visual UI
└── requirements.txt        # Dependencies
Built with ❤️ for the Archestra Hackathon 2026
