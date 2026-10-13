# LifeOS AI 🧠

LifeOS AI is a production-ready, AI-first Personal Operating System designed to act as an intelligent Chief of Staff. It coordinates tasks, schedules, habits, goals, notes (second brain), projects, and competitions under a unified executive dashboard.

## 🚀 Key Features

1. **Dashboard & Executive Briefing**: Daily calendar overview, task statuses, habit streaks, project milestones, and an AI-generated day briefing.
2. **AI Task Manager**: Kanban board with support for Natural Language Processing (NLP) quick task parsing.
3. **Smart Scheduler & Calendar**: 2-way Google Calendar synchronization integrated with target email: **anandhappriya@gmail.com**. Includes heuristic conflict detection and scheduling warnings.
4. **Competitions Tracker**: Track slides (PPT), report submissions, demo links, GitHub repo status, and teammate details.
5. **Second Brain Notes**: Keep markdown-formatted ideas and notes, and run one-click AI summaries.
6. **Habits & Goals Tracker**: Gamified habits with streak counters and long-term goal milestone progression.
7. **Interactive AI Chief of Staff**: A floating chat assistant window that lets you directly query the AI agent.

---

## 🛠️ Technology Stack

* **Frontend**: Next.js 15 (App Router), React 19, Tailwind CSS v4, Lucide Icons, Framer Motion.
* **Backend**: FastAPI, Python 3.11.9, SQLAlchemy.
* **Database**: SQLite (default local fallback for offline-first operation) or PostgreSQL (Supabase ready).
* **AI Support**: OpenAI API client (default) with offline rule-based heuristic parsing & sync fallbacks.

---

## 💻 Local Setup & Run instructions

### Prerequisites
* Node.js v24.3.0+ & npm 11.4.2+
* Python 3.11.9+

### 1. Running the FastAPI Backend
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Initialize virtual environment and install packages:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Boot up the server:
   ```bash
   venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend server runs at [http://127.0.0.1:8000](http://127.0.0.1:8000) and documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 2. Running the Next.js Frontend
1. Open another terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install client dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) to view the LifeOS AI dashboard workspace.

---

## ⚙️ Environmental Configuration

Create a `.env` file in the `backend/` directory with the following variables:

```ini
PROJECT_NAME="LifeOS AI"
DATABASE_URL="sqlite:///./lifeos.db"
SECRET_KEY="super-secret-key-lifeos-ai-2026"
OPENAI_API_KEY="your-openai-api-key"
CALENDAR_EMAIL="anandhappriya@gmail.com"
```

* *Offline-First Fallback*: If `OPENAI_API_KEY` is not provided, the platform automatically switches to local heuristic parsing and analysis modes to prevent service interruptions.
