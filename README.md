#  FrameWork - AI Pre-Production Suite

An intelligent multi-agent system for filmmakers that automates pre-production workflows by generating professional scripts, cinematic storyboards with AI-generated images, and detailed shot lists.

---

##  Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution](#-solution)
- [Architecture](#-architecture)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Setup Instructions](#-setup-instructions)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [AI Agent Concepts](#-ai-agent-concepts-used)
- [Contributing](#-contributing)

---

##  Problem Statement

Film pre-production is time-consuming and requires multiple specialized skills:
- **Scriptwriting** requires narrative structure and dialogue expertise
- **Storyboarding** needs visual storytelling and artistic skills
- **Shot lists** demand technical cinematography knowledge

**Challenges:**
- Time-intensive manual creation process
- Requires diverse skillsets (writer, artist, cinematographer)
- Difficult to visualize concepts before production
- Expensive to hire professionals for each task

---

##  Solution

**FrameWork** is an AI-powered multi-agent system that automates the entire pre-production pipeline:

1. **Intelligent Classification** - Understands what the user already has vs. what needs to be generated
2. **Script Generation** - Creates professional screenplays using Google Gemini Pro
3. **Visual Storyboarding** - Generates scene breakdowns with AI-generated cinematic images (Pollinations.AI)
4. **Technical Shot Lists** - Produces detailed camera specifications and equipment breakdowns
5. **Real-Time Updates** - WebSocket-powered live progress tracking

**Result:** From a simple prompt to complete pre-production materials in minutes, not days.

---

##  Architecture

### System Architecture Overview

```
+------------------------------------------------------------------+
|                   Frontend (Next.js/React)                       |
|                                                                  |
|  +-------------+  +---------------+  +--------------------+     |
|  | Home Page   |  | Project Page  |  | Components         |     |
|  | (Creation)  |  | (Dashboard)   |  | - ScriptView       |     |
|  |             |  |               |  | - StoryboardView   |     |
|  |             |  |               |  | - ShotListView     |     |
|  +-------------+  +---------------+  +--------------------+     |
|         |                  |                   |                 |
|         +------------------+-------------------+                 |
|                            |                                     |
|                   HTTP REST + WebSocket                          |
+----------------------------+------------------------------------|
                             |
+----------------------------+------------------------------------|
|                    Backend (FastAPI)                             |
|                                                                  |
|  +----------------------------------------------------------+   |
|  |              API Layer (main.py)                         |   |
|  |                                                          |   |
|  |  POST /projects/create                                   |   |
|  |  GET  /projects/{id}                                     |   |
|  |  POST /projects/{id}/run                                 |   |
|  |  PUT  /projects/{id}/script          (triggers change)   |   |
|  |  WS   /ws/{id}                                           |   |
|  +----------------------------------------------------------+   |
|                            |                                     |
|  +----------------------------------------------------------+   |
|  |         Orchestrator (Pipeline + Router)                 |   |
|  |                                                          |   |
|  |  Pipeline:                                               |   |
|  |  - Sequential execution                                  |   |
|  |  - Dependency management                                 |   |
|  |  - skip_script parameter                                 |   |
|  |                                                          |   |
|  |  Router:                                                 |   |
|  |  - Classification routing                                |   |
|  |  - Agent sequence determination                          |   |
|  +----------------------------------------------------------+   |
|                            |                                     |
|  +----------------------------------------------------------+   |
|  |              Multi-Agent System (5 Agents)               |   |
|  |                                                          |   |
|  |  +------------------+  +---------------------------+     |   |
|  |  | InputClassifier  |  | ChangeDetectionAgent      |     |   |
|  |  | (Gemini Pro)     |  | (Gemini Pro)              |     |   |
|  |  |                  |  |                           |     |   |
|  |  | - Analyzes input |  | - Analyzes script diffs   |     |   |
|  |  | - Detects user   |  | - Calculates change %     |     |   |
|  |  |   content        |  | - Evaluates significance  |     |   |
|  |  | - Extracts data  |  | - Decides: regenerate?    |     |   |
|  |  +------------------+  +---------------------------+     |   |
|  |                                                          |   |
|  |  +----------------+  +------------------+                |   |
|  |  | ScriptAgent    |  | StoryboardAgent  |                |   |
|  |  | (Gemini Pro)   |  | (Gemini Pro +    |                |   |
|  |  |                |  |  Pollinations)   |                |   |
|  |  | - Generates    |  |                  |                |   |
|  |  |   screenplay   |  | - Parses script  |                |   |
|  |  | - Formats      |  | - Generates imgs |                |   |
|  |  +----------------+  +------------------+                |   |
|  |                                                          |   |
|  |  +----------------+                                      |   |
|  |  | ShotListAgent  |                                      |   |
|  |  | (Gemini Pro)   |                                      |   |
|  |  |                |                                      |   |
|  |  | - Technical    |                                      |   |
|  |  |   breakdown    |                                      |   |
|  |  | - Camera specs |                                      |   |
|  |  +----------------+                                      |   |
|  +----------------------------------------------------------+   |
|                            |                                     |
|  +----------------------------------------------------------+   |
|  |        Database Layer (MongoDB)                          |   |
|  |                                                          |   |
|  |  - Project persistence                                   |   |
|  |  - Script versions (for change detection)                |   |
|  |  - State management                                      |   |
|  |  - Stage tracking (pending/running/done/failed)          |   |
|  +----------------------------------------------------------+   |
|                                                                  |
|  +----------------------------------------------------------+   |
|  |        WebSocket Manager                                 |   |
|  |                                                          |   |
|  |  - Real-time progress broadcasts                         |   |
|  |  - Connection management                                 |   |
|  |  - Heartbeat (ping/pong)                                 |   |
|  +----------------------------------------------------------+   |
+------------------------------------------------------------------+
```

### Sequential Agent Pipeline (Initial Generation)

```
                          User Input
                               |
                               v
                    +---------------------+
                    | InputClassifier     |
                    | (Gemini Pro)        |
                    |---------------------|
                    | - Analyzes prompt   |
                    | - Detects content   |
                    | - Extracts scripts  |
                    +---------------------+
                               |
                               v
                    +---------------------+
                    | ScriptAgent         |
                    | (Gemini Pro)        |
                    |---------------------|
                    | - Generates script  |
                    | - Formats properly  |
                    +---------------------+
                               |
                               v
                    +---------------------+
                    | StoryboardAgent     |
                    | (Gemini + Pollinate)|
                    |---------------------|
                    | - Parses script     |
                    | - Generates images  |
                    | - 8-15 frames       |
                    +---------------------+
                               |
                               v
                    +---------------------+
                    | ShotListAgent       |
                    | (Gemini Pro)        |
                    |---------------------|
                    | - Technical breakdown|
                    | - Camera specs      |
                    +---------------------+
                               |
                               v
                         Final Output
              (Script + Storyboard + Shot List)
```

### Loop Agent Pipeline (Edit Script Workflow)

```
                    User Edits Script in UI
                               |
                               v
                    +---------------------+
                    | Frontend sends      |
                    | PUT /script         |
                    | with new content    |
                    +---------------------+
                               |
                               v
                    +-------------------------+
                    | ChangeDetectionAgent    |
                    | (Gemini Pro)            |
                    |-------------------------|
                    | 1. Calculate diff       |
                    |    (old vs new script)  |
                    | 2. Count changes        |
                    | 3. Calculate %          |
                    | 4. LLM analyzes         |
                    |    semantic meaning     |
                    | 5. Evaluate impact      |
                    +-------------------------+
                               |
                    +----------+----------+
                    |                     |
                    v                     v
          +------------------+    +------------------+
          | Minor Changes    |    | Significant      |
          | (<3% or typos)   |    | Changes          |
          |                  |    | (>3% or scenes)  |
          | DECISION:        |    |                  |
          | Skip Regen       |    | DECISION:        |
          +------------------+    | Regenerate       |
                    |             +------------------+
                    |                     |
                    v                     v
          +------------------+    +---------------------------+
          | Save script      |    | 1. Save script            |
          | Return success   |    | 2. Clear storyboard       |
          | No pipeline run  |    | 3. Clear shot list        |
          +------------------+    | 4. Run Pipeline           |
                                  |    (skip_script=True)     |
                                  +---------------------------+
                                              |
                                              v
                                  +---------------------------+
                                  | Pipeline executes:        |
                                  |                           |
                                  | StoryboardAgent           |
                                  |      (regenerates)        |
                                  |         |                 |
                                  |         v                 |
                                  | ShotListAgent             |
                                  |      (regenerates)        |
                                  +---------------------------+
                                              |
                                              v
                                  +---------------------------+
                                  | WebSocket broadcasts      |
                                  | progress to frontend      |
                                  | (real-time updates)       |
                                  +---------------------------+
                                              |
                                              v
                                        Updated Output
                           (Same Script + New Storyboard + New Shot List)
```

---

##  Features

### Core Functionality

-  **AI Script Generation** - Professional screenplays with proper formatting
-  **Editable Scripts with Smart Regeneration** - Edit scripts in-place, AI analyzes changes and auto-regenerates storyboard/shot list if needed
-  **AI Storyboard Creation** - Visual breakdowns with generated images
-  **Shot List Automation** - Technical cinematography specifications
-  **Intelligent Classification** - Detects user-provided content vs. generation needs
-  **Real-Time Progress** - WebSocket updates during generation
-  **Auto-Pipeline Execution** - Pipeline starts automatically on project creation
-  **Content Preservation** - Never rewrites user-provided scripts

### Technical Features

-  **Multi-Agent System** - 5 LLM-powered agents (Script, Storyboard, Shot List, Classifier, Change Detection)
-  **Loop Agents** - Change detection triggers regeneration loop when script is edited
-  **Agent Evaluation** - AI evaluates script changes for significance before regenerating
-  **Custom Tools** - PollinationsAI for free image generation
-  **State Management** - MongoDB persistence + WebSocket sessions
-  **Error Handling** - Graceful fallbacks and safety filter management
-  **Logging & Observability** - Comprehensive console logs and progress tracking
-  **Beautiful UI** - Modern design with custom color palette

---

##  Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Google Gemini Pro** - LLM for script, storyboard, and shot list generation
- **Pollinations.AI** - Free text-to-image generation
- **MongoDB** - NoSQL database for persistence
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation and settings management
- **WebSockets** - Real-time communication

### Frontend
- **Next.js 14** - React framework
- **React 18** - UI library
- **Tailwind CSS** - Utility-first CSS
- **WebSocket API** - Real-time updates

### DevOps
- **Uvicorn** - ASGI server
- **Python venv** - Dependency isolation

---

##  Setup Instructions

### Prerequisites

- **Python 3.10+** (Python 3.11+ recommended)
- **Node.js 16+** and npm
- **MongoDB** (local or cloud instance)
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd FrameWork
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=frameworkdb

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# WebSocket Configuration
WEBSOCKET_HEARTBEAT_INTERVAL=30

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Important:** Replace `your_gemini_api_key_here` with your actual Gemini API key.

#### Start MongoDB

**Using Docker:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Or use local MongoDB:**
```bash
mongod --dbpath /path/to/data
```

#### Start Backend Server

**Option 1: Using the startup script**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**Option 2: Manual start**
```bash
cd app/backend
source ../../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd app/frontend
npm install
```

#### Configure Environment Variables

Create `app/frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

#### Start Frontend Server

**Option 1: Using the startup script**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

**Option 2: Manual start**
```bash
cd app/frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

##  Usage

### Creating a Project

1. **Navigate to** `http://localhost:3000`
2. **Enter a prompt** describing your film project:
   ```
   A sci-fi short film about an AI discovering emotions. 
   Should be 5 minutes, dramatic tone, visually stunning.
   ```
3. **Click "Create Project"**
4. **Pipeline auto-starts** and generates:
   - Professional screenplay
   - 8-15 storyboard frames with images
   - Technical shot list with camera specs

### Providing Your Own Script

If you already have a script and want storyboard/shot list:

```
Here's my script:

FADE IN:

INT. LABORATORY - NIGHT

A scientist works late...

FADE OUT.

Generate a storyboard and shot list from this.
```

**System will:**
-  Detect and extract your script
-  Mark script as "done" (user-provided)
-  Generate only storyboard and shot list
-  Never rewrite your original script

### Editing Scripts with Smart Regeneration

After generation, you can edit the script directly in the UI:

1. **Click "Edit Script"** button
2. **Make your changes** in the text editor
3. **Click "Save Changes"**

**What happens next:**
-  **AI analyzes your changes** - Compares old vs. new script
-  **Calculates impact** - Determines change percentage and significance
-  **Makes intelligent decision:**
  - **Minor edits (<3%)** → Script saved, no regeneration
  - **Typo fixes** → Script saved, no regeneration
  - **New scenes** → Automatically regenerates storyboard + shot list
  - **Character/location changes** → Automatically regenerates
  - **Dialogue tweaks** → Evaluated semantically

**Example:**
```
Original: "The hero walks slowly..."
Edited:   "The hero runs quickly..."

Analysis:  Significant change (motion affects visuals)
Action:    Regenerating storyboard and shot list
```

**Example:**
```
Original: "The hero walks slowly..."
Edited:   "The hero walks slowley..."  [typo fix]

Analysis:  Insignificant change (typo only)
Action:    Saved, no regeneration needed
```

### Real-Time Progress

Watch the generation happen live:
- **Script** - See text appear in real-time
- **Storyboard** - Images load as they're generated
- **Shot List** - Table populates with rows

**No refresh needed!** Everything updates automatically via WebSocket.

---

##  API Reference

### REST Endpoints

#### Create Project
```http
POST /projects/create
Content-Type: application/json

{
  "user_prompt": "Your film description",
  "title": "Optional project title"
}

Response: {
  "_id": "project_id",
  "status": "created",
  ...
}
```

#### Get Project
```http
GET /projects/{project_id}

Response: {
  "_id": "project_id",
  "script": "...",
  "storyboard": [...],
  "shot_list": [...],
  ...
}
```

#### Run Pipeline
```http
POST /projects/{project_id}/run
Content-Type: application/json

{
  "force_rerun": false
}

Response: {
  "message": "Pipeline started",
  "project_id": "..."
}
```

#### Update Script (with Smart Regeneration)
```http
PUT /projects/{project_id}/script
Content-Type: application/json

{
  "script": "FADE IN:\n\nINT. NEW SCENE - DAY..."
}

Response (if changes are significant): {
  "message": "Script updated and regeneration started",
  "project_id": "...",
  "should_regenerate": true,
  "regenerate_storyboard": true,
  "regenerate_shot_list": true,
  "reason": "Scene-level changes detected",
  "change_summary": "Added new scene, modified dialogue",
  "change_percentage": 18.5
}

Response (if changes are minor): {
  "message": "Script updated (no regeneration needed)",
  "project_id": "...",
  "should_regenerate": false,
  "reason": "Minor typo fixes only",
  "change_summary": "3 typos corrected",
  "change_percentage": 1.2
}
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{project_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  // Progress update
  if (data.type === 'progress') {
    console.log(`${data.stage}: ${data.status}`);
  }
  
  // Completion
  if (data.type === 'completed') {
    console.log('Pipeline completed!');
  }
};

// Heartbeat
setInterval(() => ws.send('ping'), 30000);
```

---

##  Project Structure

```
FrameWork/
 app/
    backend/
       main.py                      # FastAPI application entry point
       config/
          settings.py              # Environment configuration
       models/
          schemas.py               # Pydantic data models
          project_status.py        # Status enums
       database/
          mongodb.py               # MongoDB connection manager
          project_repo.py          # CRUD operations
       agents/
          script_agent.py          #  Script generation (Gemini)
          storyboard_agent.py      #  Storyboard generation (Gemini + Pollinations)
          shot_list_agent.py       #  Shot list generation (Gemini)
          change_detection_agent.py #  Script change analysis (Gemini)
       classifiers/
          input_classifier.py      #  Content classification (Gemini)
       orchestrator/
          router.py                # Classification & routing logic
          pipeline.py              # Sequential agent orchestration
       websocket/
          progress.py              # WebSocket manager for real-time updates
       utils/
           image_generation.py      #  PollinationsAI custom tool
   
    frontend/
        pages/
           index.js                 # Home page (project creation)
           project/[id].js          # Project dashboard page
        components/
           ProjectDashboard.jsx     # Main dashboard layout
           ScriptView.jsx           # Script display component
           StoryboardView.jsx       # Storyboard grid display
           ShotListView.jsx         # Shot list table
        hooks/
            useProjectStatus.js      # WebSocket hook for real-time updates

 .env                                 # Environment variables (create this)
 requirements.txt                     # Python dependencies
 start_backend.sh                     # Backend startup script
 start_frontend.sh                    # Frontend startup script
 README.md                            # This file
```

---

##  AI Agent Concepts Used

This project demonstrates several advanced AI agent concepts:

###  **1. Multi-Agent System**

- **Sequential Agents** 
  - 5 LLM-powered agents execute in strict dependency order
  - Script → Storyboard → Shot List
  - Each agent depends on the previous agent's output
  - Orchestrated by `Pipeline` class

- **Loop Agents**
  - Script edits trigger change detection
  - System can loop back and regenerate downstream artifacts
  - Intelligent looping based on significance analysis
  - Prevents infinite loops with smart evaluation

- **Agent Powered by LLM** 
  - `InputClassifier` - Analyzes user input (Gemini Pro)
  - `ScriptAgent` - Generates screenplays (Gemini Pro)
  - `StoryboardAgent` - Creates visual breakdowns (Gemini Pro)
  - `ShotListAgent` - Produces technical specs (Gemini Pro)
  - `ChangeDetectionAgent` - Evaluates script edits (Gemini Pro)

###  **2. Custom Tools**

- **PollinationsAI Integration** 
  - Custom tool for text-to-image generation
  - Zero-cost, no API key required
  - Generates cinematic storyboard images
  - Located in `app/backend/utils/image_generation.py`

###  **3. Long-Running Operations**

- **Background Tasks** 
  - Pipeline runs asynchronously using FastAPI's `BackgroundTasks`
  - WebSocket provides progress updates during execution
  - Non-blocking user experience

###  **4. Sessions & Memory**

- **Session Management** 
  - WebSocket session management via `WebSocketManager`
  - Persistent connections across component re-renders
  - Global WebSocket cache for React Strict Mode compatibility

- **Persistent State** 
  - MongoDB stores all project data
  - Classification results saved
  - Stage status tracking (pending/running/done/failed)
  - Long-term project history

###  **5. Agent Evaluation** 

- **Change Significance Analysis**
  - `ChangeDetectionAgent` evaluates script edits
  - Determines if changes warrant regeneration
  - Uses both LLM analysis and heuristics
  - Calculates change percentage and semantic impact

- **Smart Decision Making**
  - < 3% changes → Skip regeneration
  - Scene-level changes → Always regenerate
  - Typo fixes → Skip regeneration
  - New characters/locations → Regenerate

###  **6. Observability**

- **Logging** 
  - Comprehensive console logging with emojis
  - Stage-specific progress messages
  - Error tracking and reporting
  - WebSocket-broadcasted status updates

- **Tracing**  (Basic)
  - Execution flow tracking via logs
  - Pipeline stage monitoring
  - Real-time progress visualization

---

##  Features in Detail

### 1. Intelligent Input Classification

The `InputClassifier` uses Gemini Pro to analyze user prompts and determine:
- Does the user already have a script?
- Does the user want a storyboard generated?
- Does the user want a shot list?

**Examples:**

```
Input: "Write a script about robots"
→ Classification: {script: false, storyboard: false, shot_list: false}
→ Generates: Script + Storyboard + Shot List

Input: "Here's my script: FADE IN... Generate storyboard"
→ Classification: {script: true, storyboard: false, shot_list: false}
→ Generates: Storyboard only (script preserved)
```

### 2. Script Generation

- Professional screenplay format
- Proper scene headings (INT./EXT.)
- Natural dialogue
- Industry-standard formatting
- FADE IN/FADE OUT markers
- Configurable length based on user requirements

### 3. Storyboard Generation

- 8-15 key visual frames
- Scene descriptions with cinematography details
- Camera angles for each frame
- Dialogue integration
- **AI-Generated Images** via Pollinations.AI (free, no API key)
- Cinematic prompts for realistic film frames

### 4. Shot List Generation

- 1:1 minimum ratio with storyboard frames
- Shot types (Wide, Medium, Close-Up, etc.)
- Scene identifiers
- Technical descriptions
- Duration estimates
- Equipment summary

### 5. Real-Time Updates

- WebSocket connection per project
- Live progress tracking
- Auto-refresh when stages complete
- Persistent connections across page reloads
- Heartbeat mechanism (ping/pong every 30s)

---

##  Workflow Examples

### Scenario 1: Generate Everything from Scratch

**User Input:**
```
A romantic comedy about two chefs competing in a cooking competition 
but falling in love. Should be lighthearted, 8 minutes long.
```

**System Execution:**

```
1. Classification (2 seconds)
    Detected: User has nothing, needs everything
   → Sequence: [script, storyboard, shot_list]

2. Script Agent (15-20 seconds)
   ⏳ Generating professional screenplay...
    8-page script with dialogue and scene descriptions
    WebSocket: "Script generation complete"

3. Storyboard Agent (40-60 seconds)
   ⏳ Parsing script into visual frames...
   ⏳ Generating 12 cinematic images...
    12 storyboard frames with images
    WebSocket: "Storyboard generation complete"

4. Shot List Agent (20-30 seconds)
   ⏳ Creating technical breakdown...
    12+ shots with camera specs
    WebSocket: "Shot list generation complete"

Total Time: ~80-110 seconds
```

### Scenario 2: User Provides Script

**User Input:**
```
Here's my script:

FADE IN:

INT. COFFEE SHOP - DAY

SARAH, 30s, sits alone...

FADE OUT.

Generate storyboard and shot list.
```

**System Execution:**

```
1. Classification (2 seconds)
    Detected: User provided script
    Extracted and saved user's script
    Marked script stage as DONE
   → Sequence: [storyboard, shot_list]

2. Storyboard Agent (40-60 seconds)
   ⏳ Using user's script...
    10 storyboard frames with images

3. Shot List Agent (20-30 seconds)
    10 shots from storyboard

Total Time: ~60-90 seconds (faster, skipped script!)
```

### Scenario 3: Edit Script with Smart Regeneration

**User Action:**
```
User clicks "Edit Script" and makes changes:

OLD:
INT. COFFEE SHOP - DAY
SARAH sits alone reading.

NEW:
INT. COFFEE SHOP - NIGHT
SARAH sits alone reading.
TOM enters, approaches her table.
```

**System Execution:**

```
1. Change Detection (3-5 seconds)
    Analyzing differences...
    Detected changes:
      - Time of day: DAY → NIGHT
      - New character: TOM introduced
      - Scene structure modified
   
   Analysis Result:
   {
     "should_regenerate": true,
     "reason": "Time change affects lighting, new character affects framing",
     "change_percentage": 22.5%
   }

2. Script Update (instant)
    New script saved to database

3. Selective Regeneration (60-80 seconds)
   ⏭  Skipping script generation (already saved)
    Regenerating storyboard...
      - Adjusting for NIGHT lighting
      - Adding frames for TOM
    12 new storyboard frames

    Regenerating shot list...
      - Over-the-shoulder shots for TOM
      - Lighting equipment for night scene
    14 new shots

4. Complete
    All artifacts updated
    WebSocket notifies frontend in real-time

Total Time: ~65-90 seconds (smart regeneration!)
```

**Alternate Example: Minor Edit (No Regeneration)**

```
User changes:
OLD: "SARAH sits alone reading."
NEW: "SARAH sits alone, reading quietly."

Change Detection:
{
  "should_regenerate": false,
  "reason": "Minor dialogue addition, no visual impact",
  "change_percentage": 2.1%
}

Result:
 Script saved
 No regeneration (visuals unchanged)
 Instant update
```

---

##  Color Palette

The UI uses a carefully selected color scheme:

- **Palladian (#EEE9DF)** - Warm background
- **Blue Fantastic (#2C3B4D)** - Primary headers
- **Abyssal Anchorfish Blue (#1B2632)** - Deep accents
- **Burning Flame (#FFB162)** - CTAs and highlights
- **Truffle Trouble (#A35139)** - Secondary accents
- **Oatmeal (#C9C1B1)** - Borders and neutrals

---

##  Security & Safety

### Content Safety

All agents configured with relaxed safety settings for creative filmmaking:
```python
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
```

**Rationale:** Filmmaking often involves dramatic, violent, or mature themes. These settings allow creative freedom while maintaining fallback mechanisms.

### API Key Security

-  API keys stored in `.env` file (not committed to git)
-  Environment variables loaded via Pydantic settings
-  `.gitignore` prevents accidental commits

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

##  Troubleshooting

### Backend Issues

**Issue: "API Key not found"**
- Verify `.env` file is in project root
- Check `GEMINI_API_KEY` is set correctly
- Run diagnostic: `python check_api_key.py`

**Issue: MongoDB connection failed**
- Ensure MongoDB is running
- Check `MONGODB_URL` in `.env`
- Verify MongoDB port (default: 27017)

**Issue: "Model not found" error**
- Gemini model names change over time
- Run: `python list_models.py` to see available models
- Update model names in agents if needed

### Frontend Issues

**Issue: WebSocket disconnects**
- Check backend is running
- Verify `NEXT_PUBLIC_WS_URL` in `.env.local`
- Check browser console for errors

**Issue: Content not updating**
- WebSocket should auto-reconnect
- Check connection indicator (green dot)
- Try creating a new project

**Issue: Images not loading**
- Pollinations.AI is free and doesn't require API keys
- Check internet connection
- Images are loaded directly from `https://image.pollinations.ai/`

---

##  Testing

### Manual Testing

```bash
# Test backend health
curl http://localhost:8000/health

# Test project creation
curl -X POST http://localhost:8000/projects/create \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "A short film about space"}'
```

### Agent Testing

```bash
# Test agents standalone
python test_agents.py
```

---

##  Data Models

### Project Document

```typescript
{
  _id: string,
  title: string,
  user_prompt: string,
  status: "created" | "processing" | "completed" | "failed",
  
  classification: {
    script: boolean,      // User has script?
    storyboard: boolean,  // User has storyboard?
    shot_list: boolean    // User has shot list?
  },
  
  script_stage: {
    status: "pending" | "running" | "done" | "failed",
    started_at: Date | null,
    completed_at: Date | null,
    error: string | null
  },
  
  script: string | null,
  storyboard: Frame[] | null,
  shot_list: Shot[] | null,
  
  created_at: Date,
  updated_at: Date
}
```

### Storyboard Frame

```typescript
{
  frame_number: number,
  scene: string,
  description: string,
  camera_angle: string,
  dialogue: string,
  image_url: string,
  notes: string
}
```

### Shot

```typescript
{
  shot_number: number,
  scene: string,
  shot_type: string,
  camera_movement: string,
  description: string,
  duration: string,
  equipment: string[],
  lens: string,
  notes: string
}
```

---

##  Error Handling

The system includes comprehensive error handling:

### Graceful Degradation

- **Safety Filter Blocks**: Falls back to keyword-based classification
- **JSON Parsing Errors**: Multiple cleanup strategies + retry logic
- **Agent Failures**: Generates basic fallback content
- **WebSocket Disconnects**: Auto-reconnect with exponential backoff

### Logging

All errors are logged with:
-  Error emoji for visibility
- Detailed error messages
- Stack traces for debugging
- WebSocket broadcasts for frontend awareness

---

##  Key Design Decisions

### 1. Sequential vs. Parallel Agents

**Chosen:** Sequential execution

**Rationale:**
- Storyboard requires script as input
- Shot list requires storyboard as input
- Dependencies enforce sequential order
- Simpler to debug and maintain

### 2. Inverse Classification Logic

**Chosen:** `true` = user HAS content, `false` = needs generation

**Rationale:**
- More intuitive: "What does the user already have?"
- Easier to extend (add new content types)
- Clear separation between provided vs. generated content

### 3. WebSocket for Progress

**Chosen:** WebSocket over polling

**Rationale:**
- Real-time updates without delay
- Lower server load (no constant polling)
- Better UX (instant feedback)
- Professional appearance

### 4. Pollinations.AI for Images

**Chosen:** Pollinations.AI over commercial APIs

**Rationale:**
- Free, no API key required
- Good quality for storyboard visualization
- No rate limits or costs
- Easy integration

---

##  Complete System Flow Diagram

### Data Flow with ChangeDetectionAgent Integration

```
+-------------------------------------------------------------------+
|                        FRONTEND (React)                           |
+-------------------------------------------------------------------+
                              |
         +--------------------+---------------------+
         |                    |                     |
         v                    v                     v
   Create Project      Get Project Data      Edit Script
         |                    |                     |
         |                    |                     |
         v                    v                     v
   POST /projects/create  GET /projects/{id}  PUT /projects/{id}/script
         |                    |                     |
         |                    |                     |
+--------v--------------------v---------------------v----------------+
|                      FASTAPI BACKEND                               |
+--------------------------------------------------------------------+
         |                    |                     |
         |                    |                     |
         v                    v                     v
   +------------+      +-------------+       +-------------------+
   | Create     |      | Fetch from  |       | ChangeDetection   |
   | Project    |      | MongoDB     |       | Agent             |
   | Record     |      | Return data |       |                   |
   +------------+      +-------------+       | 1. Get old script |
         |                    ^              | 2. Compare with   |
         v                    |              |    new script     |
   +------------+             |              | 3. Calculate diff |
   | Auto-run   |             |              | 4. Analyze with   |
   | Pipeline   |             |              |    Gemini Pro     |
   +------------+             |              | 5. Decide action  |
         |                    |              +-------------------+
         |                    |                     |
         v                    |         +-----------+------------+
   +-------------------+      |         |                        |
   | PIPELINE          |      |         v                        v
   | ORCHESTRATOR      |      |   Minor Change            Significant
   +-------------------+      |   (Skip regen)            (Regenerate)
         |                    |         |                        |
         v                    |         v                        v
   +-------------------+      |   Save script            Save script
   | ROUTER            |      |   Return success         Clear storyboard
   | - Classification  |      |         |                Clear shot_list
   | - Determine       |      +---------+                Run Pipeline
   |   sequence        |                                 (skip_script=True)
   +-------------------+                                         |
         |                                                       |
         v                                                       v
   +-------------------+                              +-------------------+
   | Agent Sequence    |                              | Agent Sequence    |
   | (Initial)         |                              | (Regeneration)    |
   +-------------------+                              +-------------------+
         |                                                       |
         v                                                       |
   IF script=false:                                              |
   +-------------------+                                         |
   | ScriptAgent       |                                         |
   | (Gemini Pro)      |                                         |
   | - Generate script |                                         |
   | - Save to DB      |                                         |
   +-------------------+                                         |
         |                                                       |
         v<------------------------------------------------------+
   IF storyboard=false:
   +-------------------+
   | StoryboardAgent   |
   | (Gemini Pro +     |
   |  Pollinations)    |
   | - Parse script    |
   | - Generate frames |
   | - Generate images |
   | - Save to DB      |
   +-------------------+
         |
         v
   IF shot_list=false:
   +-------------------+
   | ShotListAgent     |
   | (Gemini Pro)      |
   | - Analyze frames  |
   | - Technical specs |
   | - Save to DB      |
   +-------------------+
         |
         v
   +-------------------+
   | Mark Complete     |
   | Update status     |
   +-------------------+
         |
         v
   +-------------------+
   | WebSocket Manager |
   | - Broadcasts      |
   |   progress at     |
   |   each step       |
   +-------------------+
         |
         v
+--------------------------------------------------------------------+
|                      MONGODB DATABASE                              |
|                                                                    |
|  - Projects Collection                                             |
|    - _id, title, user_prompt                                       |
|    - script (versioned for change detection)                       |
|    - storyboard (array of frames with images)                      |
|    - shot_list (array of technical shots)                          |
|    - classification (what user provided)                           |
|    - script_stage, storyboard_stage, shot_list_stage              |
|    - status (created/processing/completed/failed)                  |
+--------------------------------------------------------------------+
         |
         v (Real-time updates)
+--------------------------------------------------------------------+
|                   WEBSOCKET CONNECTION                             |
|                                                                    |
|  - Persistent connection per project                               |
|  - Heartbeat (ping/pong every 30s)                                 |
|  - Progress messages: {stage, status, message}                     |
|  - Triggers frontend re-render on updates                          |
+--------------------------------------------------------------------+
         |
         v
+--------------------------------------------------------------------+
|                      FRONTEND (React)                              |
|                                                                    |
|  useProjectStatus Hook:                                            |
|  - Maintains WebSocket connection                                  |
|  - Updates status state                                            |
|  - Triggers data refresh via lastUpdate                            |
|                                                                    |
|  ProjectDashboard Component:                                       |
|  - Fetches latest data when lastUpdate changes                     |
|  - Re-renders with new script/storyboard/shot_list                 |
|                                                                    |
|  ScriptView Component:                              |
|  - "Edit Script" button                                            |
|  - Textarea editor                                                 |
|  - "Save Changes" triggers PUT /script                             |
|  - Shows analysis result (regenerate or skip)                      |
|  - Shows real-time regeneration progress                           |
+--------------------------------------------------------------------+
```

### Key Integration Points for ChangeDetectionAgent

1. **Entry Point**: `PUT /projects/{id}/script` endpoint in `main.py`
2. **Invocation**: Called before pipeline execution to analyze changes
3. **Decision Making**: Returns `should_regenerate` boolean
4. **Pipeline Control**: If true, pipeline runs with `skip_script=True`
5. **Database**: Compares current script (from DB) vs. new script (from request)
6. **Feedback Loop**: Results sent back to frontend for user notification

---

##  Advanced Features

### Content Preservation

If user provides a script:
-  Script is extracted and saved AS-IS
-  Script agent is SKIPPED (not run)
-  Script stage marked as DONE immediately
-  Only requested outputs are generated
-  Original script NEVER rewritten

### JSON Output Enforcement

```python
generation_config={
    "temperature": 0.7,
    "top_p": 0.9,
    "max_output_tokens": 4000,
    "response_mime_type": "application/json",  # Forces valid JSON
}
```

### Robust JSON Parsing

Multiple cleanup strategies:
1. Remove markdown code blocks
2. Strip trailing commas
3. Remove text before/after JSON
4. Fix single quotes → double quotes
5. Retry with error logging

### Automatic Shot Validation

Ensures shot count matches storyboard frame count:
```python
if len(shot_list) < len(storyboard):
    # Auto-generate missing shots from remaining frames
    for i in range(len(shot_list), len(storyboard)):
        shot_list.append(create_shot_from_frame(storyboard[i]))
```

---

##  Performance

- **Script Generation:** ~15-20 seconds
- **Storyboard Generation:** ~40-60 seconds (with images)
- **Shot List Generation:** ~20-30 seconds
- **Total Pipeline:** ~80-110 seconds (from scratch)
- **With User Script:** ~60-90 seconds (skips script generation)

---

##  Development

### Running in Development Mode

**Terminal 1 - Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start_frontend.sh
```

### Hot Reload

Both backend and frontend support hot reload:
- Backend: Uvicorn `--reload` flag
- Frontend: Next.js automatic refresh

### Debugging

**Backend logs:**
```bash
# Watch backend terminal for:
 Gemini API key loaded
 Starting pipeline for project...
 Generating script...
 Script generated successfully
```

**Frontend console:**
```javascript
// Open DevTools (F12) to see:
 Creating new WebSocket connection...
 WebSocket connected
 WebSocket message: {type: 'progress', ...}
 Project data refreshed
```

---

##  Dependencies

### Backend (`requirements.txt`)

```
fastapi>=0.109.0
uvicorn>=0.27.0
motor>=3.3.2
pydantic>=2.5.3
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
httpx>=0.26.0
```

### Frontend (`package.json`)

```json
{
  "dependencies": {
    "next": "14.x",
    "react": "18.x",
    "react-dom": "18.x"
  },
  "devDependencies": {
    "tailwindcss": "^3.x",
    "autoprefixer": "^10.x",
    "postcss": "^8.x"
  }
}
```

---

##  Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use environment variables for all secrets
- [ ] Set up MongoDB authentication
- [ ] Configure CORS for production domain
- [ ] Use process manager (PM2, systemd)
- [ ] Set up HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Set up monitoring and alerts

### Docker Deployment (Future)

```dockerfile
# Example Dockerfile (not yet implemented)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/backend ./app/backend
CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0"]
```

---

##  Contributing

Contributions are welcome! Areas for improvement:

- **Parallel Agents** - Run independent tasks concurrently
- **Agent Evaluation** - Metrics and quality assessment
- **Memory Bank** - Long-term context retention
- **Context Engineering** - Compaction for large inputs
- **A2A Protocol** - Agent-to-agent communication
- **Production Deployment** - Docker, cloud hosting
- **Export Features** - PDF, Final Draft, CSV
- **File Uploads** - Upload existing scripts/storyboards

---

##  License

MIT License - See LICENSE file for details

---

##  Acknowledgments

- **Google Gemini** - LLM for content generation
- **Pollinations.AI** - Free text-to-image generation
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **MongoDB** - Database persistence

---

##  Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check logs in backend/frontend terminals
- Review console output for debugging

---

**Built with love for filmmakers by filmmakers**