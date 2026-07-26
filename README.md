# 🎓 AI Personal Learning Mentor
Live Link:https://learning-mentor-ovk6zmsvzrggrcncaegmkv.streamlit.app/
An AI-powered Streamlit application that helps students create a **personalized learning roadmap** based on their current skills and career goals. Built using the **Google Gemini API** with structured JSON outputs.

---

## ✨ Features

- 📝 Simple form to collect: Name, Current Skills, Career Goal, Daily Study Hours
- 🗺️ AI-generated **Learning Roadmap** (phased, with milestones)
- 📅 **Weekly Study Plan** tailored to available study hours
- 🧠 **Recommended Skills** in priority order
- 💻 **Suggested Projects** scaled by difficulty
- 📚 **Learning Resources** (courses, docs, channels)
- 💡 **Career Tips** for landing the target role
- 📦 Guaranteed **structured JSON output** (schema-enforced, not just prompted)
- ⭐ **Bonus features:**
  - 📄 Export roadmap as PDF
  - 🕓 Save & view user history across sessions
  - 🎤 AI-generated interview questions tailored to the career goal

---

## 🏗️ Architecture

```
┌─────────────┐      ┌───────────────────┐      ┌──────────────────────┐
│   Student   │─────▶│   Streamlit UI     │─────▶│   Prompt Builder      │
│ (Name,      │      │   (app.py)         │      │  (system + user       │
│  Skills,    │◀─────│                    │◀─────│   prompt templates)   │
│  Goal, Hrs) │      └───────────────────┘      └──────────┬────────────┘
└─────────────┘               │                             │
                               │                             ▼
                               │                  ┌──────────────────────┐
                               │                  │   Google Gemini API   │
                               │                  │  (response_schema =   │
                               │                  │   forced JSON output) │
                               │                  └──────────┬────────────┘
                               │                             │
                               ▼                             ▼
                    ┌────────────────────┐        ┌──────────────────────┐
                    │  Local JSON history │        │   Structured JSON     │
                    │  (user_history.json)│◀───────│   Roadmap Response     │
                    └────────────────────┘        └──────────┬────────────┘
                                                               │
                                                               ▼
                                                  ┌──────────────────────┐
                                                  │  Rendered in UI Tabs  │
                                                  │  + JSON/PDF download  │
                                                  └──────────────────────┘
```

**Flow:**
1. Student fills the form in the Streamlit UI.
2. `build_user_prompt()` combines their inputs with a fixed system instruction (see `PROMPT_DESIGN.md`).
3. The prompt + a strict JSON `response_schema` are sent to Gemini (`gemini-2.0-flash`).
4. Gemini is forced to return valid JSON matching the schema — no manual parsing/regex needed.
5. The JSON is rendered into readable tabs (Roadmap, Weekly Plan, Skills, Projects, Resources, Tips) and can be downloaded as JSON or PDF.
6. Each generated roadmap is appended to a local `user_history.json` file.

---

## 📁 Project Structure

```
learning-mentor-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md               # This file
├── PROMPT_DESIGN.md        # Prompt engineering documentation
├── user_history.json       # Auto-created; stores past roadmap requests
└── screenshots/             # App screenshots for submission
```

---

## 🚀 Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/learning-mentor-app.git
cd learning-mentor-app
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a free Gemini API key
- Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- Sign in with Google, click "Create API Key", copy it.

### 5. Run the app
```bash
streamlit run app.py
```
The app opens automatically at `http://localhost:8501`.

### 6. Use it
- Paste your Gemini API key in the sidebar.
- Fill in your name, current skills, career goal, and daily study hours.
- Click **Generate My Roadmap**.
- Browse the tabs, and optionally download as JSON or PDF.

> 🔒 Your API key is only used locally in your session — it is never stored or sent anywhere except directly to Google's API.

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| UI | Streamlit |
| LLM | Google Gemini (`gemini-flash-latest`) via `google-genai` SDK |
| Structured Output | Gemini `response_schema` (JSON mode) |
| PDF Export | fpdf2 |
| Persistence | Local JSON file |

---

## 📸 Screenshots

_(Add screenshots of the running app here before submission — see `/screenshots` folder)_

1. Input form
2. Generated roadmap (Roadmap tab)
3. Weekly plan tab
4. PDF export

---

## 📄 Prompt Design

See [`PROMPT_DESIGN.md`](./PROMPT_DESIGN.md) for the full prompt engineering documentation — system instruction design, schema design, and reasoning behind key decisions.

---

## ⭐ Bonus Features Implemented

- ✅ Export roadmap as PDF
- ✅ Save user history (visible in sidebar, persisted in `user_history.json`)
- ✅ Generate interview questions based on the user's career goal (with difficulty level and reasoning for each)

---

## 📜 License

This project was built as an academic/internship assignment. Free to use and modify.
