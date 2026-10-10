# Code2Career — GD Arena

> **Real-Time Voice-First AI Group Discussion & Interview Simulation Arena**  
> *Campus Placement & Career Readiness Preparation Platform*

---

## What it does

**Code2Career (GD Arena)** is a voice-first AI simulation platform designed for students and job seekers to rehearse high-stakes Group Discussions (GD) and technical interview rounds in a safe, real-time environment. It pairs candidates with an autonomous AI panel of distinct personalities—ranging from aggressive interrupters to data-driven synthesizers—who debate, build, and disagree dynamically with speech-to-text live captioning. After each round, the platform delivers an honest, transcript-grounded diagnostic report quoting the student's exact statements to evaluate argument strength, listening markers, and collaborative synthesis.

* **Problem Statement Number**: **PS #02** *(AI for Career Readiness, Placement Training & Group Discussion Simulation)*

---

## Done / Left / Plan

### What works now (Done)
- **Live Voice Group Discussion Arena**: Browser-native Speech-to-Text (Web Speech API) transcription with real-time captions and typed fallback.
- **Autonomous AI Personalities**: 4 distinct panel personalities with unique discussion dynamics:
  - **Aarav / Riya (*The Dominator*)**: High-tempo speaker who interrupts with confidence and challenges weak premises.
  - **Arjun (*Data-Driven*)**: Analytical speaker demanding empirical evidence, statistics, and verifiable claims.
  - **Meera (*Quiet Builder*)**: Synthesizer who identifies common ground and resolves polarized debate.
  - **Dr. Kabir (*The Moderator*)**: Guides openings, enforces turn equity, steps in on 2-minute silences, and requests summaries.
- **Automatic Response & Debate Engine**: AI panel responds automatically with natural human conversational cadence (~1.3s delay) and continues turn-taking during quiet periods, with user interruption safeguards.
- **Dual Day & Night Theme**: Polished **Professional Blue** design system styled in Plus Jakarta Sans and JetBrains Mono typography.
- **Interactive Education Modals**: Full in-app guides for AI Panel strategy, Feedback methodology, and Scoring rubrics.
- **Multi-Lingual Practice**: Support for Indian English and 7 regional Indian languages (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi).
- **Persistent Transcript Architecture**: Relational schema in SQLite preserving turn-by-turn timestamps, speaker sources, and session phases.
- **Transcript-Grounded Scoring & Report**: Objective 1–10 scoring engine, performance tiers (Weak, Average, Strong, Elite), top 3 strengths, top 3 improvements, and verbatim quote attribution.
- **Zero-Failure Hybrid Provider Architecture**: Works offline out-of-the-box with a deterministic Mock LLM, and automatically activates Google Gemini Flash Lite, Groq Llama 3.3 70B, or OpenRouter when API keys are configured.

### What is left for the next 16 hours (Left)
- **Neural TTS Multi-Voice Pipeline**: Multi-speaker streaming voice audio integration using `edge-tts` and Gemini Live Audio for human-like auditory immersion.
- **Webcam Eye-Contact & Facial Expression AI**: Client-side MediaPipe face mesh analysis to evaluate head posture, eye contact, and confidence during turns.
- **Multiplayer Hybrid Rooms**: WebRTC/WebSocket support allowing human peers to join rooms alongside AI panelists (e.g. 2 human candidates + 2 AI co-participants).
- **Resume & Job Description Grounding**: PDF upload capability allowing candidates to simulate company-specific GD prompts tailored to targeted placement drives.
- **Cloud Production Deployment**: One-click hosted instances on Vercel (Frontend) and Render/Railway (Backend).

### Plan to finish it (Plan)
- **Hours 1–4**: Connect neural TTS audio synthesis pipeline so each AI panelist speaks aloud with distinct voice profiles and natural inflection.
- **Hours 5–8**: Integrate MediaPipe webcam eye-contact and posture confidence tracking widget into the live coach sidebar.
- **Hours 9–12**: Implement multi-room WebSocket synchronization for hybrid peer-to-peer multiplayer mock GDs.
- **Hours 13–15**: Deploy frontend to Vercel and backend to Render with automated health-checks and live URLs.
- **Hours 16**: Final end-to-end rehearsal, stress testing, pitch deck finalization, and demo video recording.

---

## Architecture and why

```
┌────────────────────────────────────────────────────────┐
│                   FRONTEND (CLIENT)                    │
│   Vanilla ES6+ · Vite · Tailwind CSS · Lucide Icons    │
│   Web Speech API (STT/TTS) · Plus Jakarta Sans Font   │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP / JSON API (CORS)
┌──────────────────────────▼─────────────────────────────┐
│                    BACKEND (SERVER)                    │
│          Python 3.11+ · Flask WSGI Server              │
│       ThreadingWSGIServer · Moderator State Machine    │
└────────────┬─────────────────────────────┬─────────────┘
             │                             │
┌────────────▼────────────┐   ┌────────────▼─────────────┐
│      SQLITE DATABASE    │   │    PROVIDER REGISTRY     │
│  Sessions · Transcripts │   │  Gemini · Groq · Mock    │
└─────────────────────────┘   └──────────────────────────┘
```

### Technical Choices & Rationale
1. **AI Model & Provider Architecture**:
   - **Why Gemini Flash Lite & Groq Llama 3.3**: Sub-second latency and high token throughput are essential for live conversational simulations. Gemini Flash Lite provides cost-effective, culturally nuanced context, while Groq delivers near-instant time-to-first-token.
   - **Why a Provider Registry with Mock Fallback**: Hackathon demos must never crash due to rate limits or wifi drops. Our architecture prioritizes reliability by running a deterministic, topic-aware offline state machine when no keys are present, while seamlessly switching to live LLMs when keys are provided.
2. **Real-Time Approach**:
   - **Why REST with Optimistic State & Scheduled Cadence**: Rather than introducing fragile WebSocket reconnection bugs during live presentations, we implemented low-latency REST endpoints with client-side reactive polling and an automatic cadence engine. It guarantees 100% transcript integrity and zero dropped turns.
3. **Data Store**:
   - **Why SQLite**: SQLite is embedded, zero-maintenance, fully ACID-compliant, and runs in-memory or on-disk without external daemon dependencies. It allows persistent transcript history, session replays, and quote attribution without database setup friction.

---

## What we added (Beyond the Brief)

- **Autonomous Auto-Debate Engine**: Rather than requiring the student to click a button for every response, the AI panel responds automatically (~1.3s delay) and continues debate turn-taking if the room goes quiet, closely simulating real group discussion dynamics.
- **Smart User-Interruption Sentinel**: Automatically detects when the student begins typing or activates the microphone, pausing the AI scheduler so panelists never speak over the candidate.
- **Inactivity Intervention Nudge**: Actively alerts candidates if they remain silent for over 2 minutes, teaching students when and how to interject in high-pressure rounds.
- **Professional Blue Dual Theme**: Complete Day (clean slate-white) and Night (deep midnight navy) design system with typography tailored for high-stakes enterprise assessment tools.
- **Educational Modalities**: In-app strategy modals explaining AI panelist behaviors, feedback quote validation rules, and scoring calculations.
- **Multi-Lingual Regional Language Matrix**: Built-in support for Indian English and 7 Indian languages to cater to diverse tier-2/tier-3 placement drives across India.

---

## How to run it

### Prerequisites
- **Node.js** (v18+) & **npm**
- **Python** (v3.11+) & **pip**

### 1. Run the Backend API Server
```bash
cd gd-arena/backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Add your AI API key
# cp .env.example .env && echo "GEMINI_API_KEY=your_key_here" >> .env

# Start Flask server (runs on http://127.0.0.1:8000)
python3 server.py
```

### 2. Run the Frontend Client
```bash
cd gd-arena/frontend

# Install dependencies
npm install

# Start Vite dev server (runs on http://localhost:5173)
npm run dev
```

### 3. Run Backend Verification Tests
```bash
cd gd-arena/backend
pytest
```

* **Test Login**: No authentication or sign-up required. Access practice rooms immediately without paywalls or login friction.
* **Local Test URL**: [http://localhost:5173](http://localhost:5173)
* **Production Deployment Ready**: Vercel configuration (`vercel.json`) is included for instantaneous static frontend deployment.

---

## Tools and AI used

- **Frontend Technologies**: Vanilla JavaScript (ES6 Modules), Vite 7, Tailwind CSS, Lucide Icons, Google Fonts (`Plus Jakarta Sans`, `JetBrains Mono`).
- **Backend Technologies**: Python 3.11+, Flask WSGI, `sqlite3`, `pytest`, `python-dotenv`, `urllib3`.
- **AI Models & Services**:
  - Google Gemini Flash Lite (`gemini-2.0-flash-lite-preview-02-05`)
  - Groq Llama 3.3 70B (`llama-3.3-70b-versatile`)
  - OpenRouter API (`meta-llama/llama-3.3-70b-instruct`)
  - Deterministic Rule-Based State Machine (Offline Mock Provider)
- **Audio & Speech APIs**: Browser Web Speech API (`SpeechRecognition` & `SpeechSynthesis`), scaffolding for `edge-tts`.
- **Transparency & Ethical AI**:
  - Every page includes a prominent notice: *"All participants are AI - 100% safe practice"*.
  - AI panelists are explicitly labeled with persona avatars, names, and behavioral roles.
  - The setup screen visibly identifies whether the session is running on Demo AI Mode or a connected live LLM provider.

---

## Who it is for

- **Engineering & MBA Students (Tier-1, Tier-2, Tier-3 Colleges)**: Group Discussions are the steepest elimination filter in campus recruitment drives (TCS, Infosys, Wipro, Cognizant, Big 4, and product firms), eliminating 60%–80% of applicants before technical interviews. Code2Career gives students an accessible simulator to practice before placement day.
- **Introverted & Anxious Candidates**: Individuals who hesitate to speak up in group settings can practice polite interjections and assertiveness without peer judgment or stage fright.
- **College Placement Cells & Training Academies**: Provides an automated, scalable mock GD tool that gives structured, transcript-backed performance data without requiring human faculty moderators for every round.

### Why Candidates Will Come Back
1. **Verbatim Quote Feedback**: Students receive specific feedback citing the exact sentences they spoke, rather than generic compliments.
2. **Quantifiable Improvement**: The 1–10 scoring scale, turn counts, word velocity, and listening metrics give candidates clear progress markers across sessions.
3. **Infinite Practice Scenarios**: Practice supportive, balanced, or challenging discussions across current affair prompts, ethical dilemmas, or custom company prompts.
