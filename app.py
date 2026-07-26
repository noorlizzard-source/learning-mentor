"""
AI Personal Learning Mentor
----------------------------
A Streamlit app that takes a student's current skills, career goal,
and available study time, then uses the Google Gemini API to generate
a personalized, structured learning roadmap (returned as JSON).

Run with:  streamlit run app.py
"""

import json
import os
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types
from fpdf import FPDF

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
HISTORY_FILE = "user_history.json"

st.set_page_config(
    page_title="AI Personal Learning Mentor",
    page_icon="🎓",
    layout="wide",
)

# ----------------------------------------------------------------------
# STRUCTURED OUTPUT SCHEMA
# This forces Gemini to return valid JSON matching this exact shape.
# ----------------------------------------------------------------------
ROADMAP_SCHEMA = {
    "type": "object",
    "properties": {
        "student_name": {"type": "string"},
        "career_goal": {"type": "string"},
        "overview": {"type": "string"},
        "learning_roadmap": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "phase": {"type": "string"},
                    "duration": {"type": "string"},
                    "focus_area": {"type": "string"},
                    "milestones": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["phase", "duration", "focus_area", "milestones"],
            },
        },
        "weekly_study_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "week": {"type": "string"},
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "daily_breakdown": {"type": "string"},
                },
                "required": ["week", "topics", "daily_breakdown"],
            },
        },
        "recommended_skills": {
            "type": "array",
            "items": {"type": "string"},
        },
        "suggested_projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "difficulty": {"type": "string"},
                },
                "required": ["title", "description", "difficulty"],
            },
        },
        "learning_resources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["title", "type", "description"],
            },
        },
        "career_tips": {
            "type": "array",
            "items": {"type": "string"},
        },
        "interview_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "why_it_matters": {"type": "string"},
                },
                "required": ["question", "difficulty", "why_it_matters"],
            },
        },
    },
    "required": [
        "student_name",
        "career_goal",
        "overview",
        "learning_roadmap",
        "weekly_study_plan",
        "recommended_skills",
        "suggested_projects",
        "learning_resources",
        "career_tips",
        "interview_questions",
    ],
}

# ----------------------------------------------------------------------
# PROMPT ENGINEERING
# ----------------------------------------------------------------------
SYSTEM_INSTRUCTION = """You are an expert career mentor and curriculum designer
with 15+ years of experience mentoring self-taught developers and students
into successful tech careers. You specialize in creating realistic,
personalized learning roadmaps.

Rules you must always follow:
1. Base the roadmap on the student's ACTUAL current skill level -- do not
   assume prior knowledge they did not mention.
2. Respect the student's stated daily study hours when building the weekly
   plan and estimating timelines. Do not suggest an unrealistic pace.
3. Recommend skills that logically bridge the gap between their current
   skills and their career goal, in the correct learning order.
4. Suggested projects must be practical, portfolio-worthy, and scaled to
   the student's level (beginner projects for beginners, harder ones later
   in the roadmap).
5. Learning resources should be genuinely well-known, high-quality, and
   relevant to the specific career goal (official docs, well-known free
   or paid courses, well-known YouTube channels/creators) -- do not invent
   fake resources.
6. Career tips should be specific and actionable, not generic platitudes.
7. Interview questions must be realistic questions an employer would
   actually ask for that specific role, ranging from beginner to
   intermediate difficulty, with a short note on why each question matters.
8. Keep language encouraging, clear, and beginner-friendly.
9. Respond ONLY with valid JSON matching the provided schema. Do not add
   any commentary, markdown formatting, or text outside the JSON object.
"""


def build_user_prompt(name, skills, goal, hours):
    return f"""Create a personalized learning roadmap for this student:

Name: {name}
Current Skills: {skills}
Career Goal: {goal}
Daily Study Hours Available: {hours}

Generate a complete roadmap following these requirements:
- learning_roadmap: 3-5 phases, each with a clear duration estimate based on
  {hours} hours/day of study, a focus area, and 2-4 concrete milestones.
- weekly_study_plan: a week-by-week plan for at least the first 4-6 weeks,
  with topics per week and how the daily hours should be split.
- recommended_skills: 5-10 skills, ordered by priority.
- suggested_projects: 3-5 projects of increasing difficulty.
- learning_resources: 5-8 real, well-known resources (courses, docs,
  channels) relevant specifically to {goal}.
- career_tips: 4-6 actionable tips for landing a role as {goal}.
- interview_questions: 6-8 realistic interview questions a candidate for
  {goal} would likely be asked, ordered from easier to harder, each with
  a difficulty label and a short note on why it matters.

Return ONLY the JSON object matching the schema."""


# ----------------------------------------------------------------------
# GEMINI CALL
# ----------------------------------------------------------------------
def generate_roadmap(api_key, name, skills, goal, hours):
    client = genai.Client(api_key=api_key)

    prompt = build_user_prompt(name, skills, goal, hours)

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ROADMAP_SCHEMA,
            temperature=0.7,
        ),
    )
    return json.loads(response.text)


# ----------------------------------------------------------------------
# BONUS FEATURE 1: SAVE USER HISTORY
# ----------------------------------------------------------------------
def save_to_history(entry):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


# ----------------------------------------------------------------------
# BONUS FEATURE 2: EXPORT ROADMAP AS PDF
# ----------------------------------------------------------------------
def export_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def heading(text):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 10, text)
        pdf.ln(1)

    def body(text):
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 7, text)
        pdf.ln(1)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "AI Personal Learning Mentor - Roadmap", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Student: {data['student_name']}  |  Goal: {data['career_goal']}", ln=True)
    pdf.ln(4)

    heading("Overview")
    body(data.get("overview", ""))

    heading("Learning Roadmap")
    for phase in data.get("learning_roadmap", []):
        body(f"- {phase['phase']} ({phase['duration']}): {phase['focus_area']}")
        for m in phase.get("milestones", []):
            body(f"    * {m}")

    heading("Weekly Study Plan")
    for week in data.get("weekly_study_plan", []):
        body(f"- {week['week']}: {', '.join(week['topics'])}")
        body(f"    Daily breakdown: {week['daily_breakdown']}")

    heading("Recommended Skills")
    body(", ".join(data.get("recommended_skills", [])))

    heading("Suggested Projects")
    for proj in data.get("suggested_projects", []):
        body(f"- {proj['title']} ({proj['difficulty']}): {proj['description']}")

    heading("Learning Resources")
    for res in data.get("learning_resources", []):
        body(f"- {res['title']} [{res['type']}]: {res['description']}")

    heading("Career Tips")
    for tip in data.get("career_tips", []):
        body(f"- {tip}")

    heading("Practice Interview Questions")
    for q in data.get("interview_questions", []):
        body(f"- ({q['difficulty']}) {q['question']}")
        body(f"    Why it matters: {q['why_it_matters']}")

    output_path = "roadmap.pdf"
    pdf.output(output_path)
    return output_path


# ----------------------------------------------------------------------
# STREAMLIT UI
# ----------------------------------------------------------------------
def main():
    st.title("🎓 AI Personal Learning Mentor")
    st.caption("Get a personalized learning roadmap generated by AI, based on your skills and career goal.")

    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("Gemini API Key", type="password", help="Get one free at aistudio.google.com/app/apikey")
        st.markdown("---")
        st.header("🕓 History")
        history = load_history()
        if history:
            for h in reversed(history[-5:]):
                st.write(f"**{h['name']}** → {h['goal']}  \n_{h['timestamp']}_")
        else:
            st.write("No past roadmaps yet.")

    st.subheader("Tell us about yourself")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name")
        goal = st.text_input("Career Goal", placeholder="e.g., Flutter Mobile App Developer")
    with col2:
        skills = st.text_area("Current Skills", placeholder="e.g., HTML, CSS, basic Python")
        hours = st.slider("Daily Study Hours", 1, 12, 2)

    generate_btn = st.button("🚀 Generate My Roadmap", type="primary", use_container_width=True)

    if generate_btn:
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
            return
        if not name or not skills or not goal:
            st.error("Please fill in your name, skills, and career goal.")
            return

        with st.spinner("Generating your personalized roadmap..."):
            try:
                data = generate_roadmap(api_key, name, skills, goal, hours)
                st.session_state["roadmap_data"] = data

                save_to_history({
                    "name": name,
                    "goal": goal,
                    "skills": skills,
                    "hours": hours,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                return

    if "roadmap_data" in st.session_state:
        data = st.session_state["roadmap_data"]

        st.success("Here's your personalized roadmap!")
        st.markdown(f"### 👋 Hi {data['student_name']}, here's your path to becoming a **{data['career_goal']}**")
        st.write(data.get("overview", ""))

        tabs = st.tabs([
            "🗺️ Roadmap", "📅 Weekly Plan", "🧠 Skills",
            "💻 Projects", "📚 Resources", "💡 Career Tips",
            "🎤 Interview Prep", "🧾 Raw JSON"
        ])

        with tabs[0]:
            for phase in data.get("learning_roadmap", []):
                with st.expander(f"**{phase['phase']}** — {phase['duration']}"):
                    st.write(f"**Focus:** {phase['focus_area']}")
                    for m in phase.get("milestones", []):
                        st.write(f"- {m}")

        with tabs[1]:
            for week in data.get("weekly_study_plan", []):
                with st.expander(f"**{week['week']}**"):
                    st.write("**Topics:** " + ", ".join(week["topics"]))
                    st.write(f"**Daily breakdown:** {week['daily_breakdown']}")

        with tabs[2]:
            for skill in data.get("recommended_skills", []):
                st.write(f"✅ {skill}")

        with tabs[3]:
            for proj in data.get("suggested_projects", []):
                st.markdown(f"**{proj['title']}** · _{proj['difficulty']}_")
                st.write(proj["description"])
                st.markdown("---")

        with tabs[4]:
            for res in data.get("learning_resources", []):
                st.markdown(f"**{res['title']}** · _{res['type']}_")
                st.write(res["description"])
                st.markdown("---")

        with tabs[5]:
            for tip in data.get("career_tips", []):
                st.write(f"💡 {tip}")

        with tabs[6]:
            st.caption("Practice questions you might be asked for this role — use these to prep before applying.")
            for q in data.get("interview_questions", []):
                with st.expander(f"**{q['question']}** · _{q['difficulty']}_"):
                    st.write(f"**Why it matters:** {q['why_it_matters']}")

        with tabs[7]:
            st.json(data)

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "⬇️ Download as JSON",
                data=json.dumps(data, indent=2),
                file_name=f"{data['student_name']}_roadmap.json",
                mime="application/json",
                use_container_width=True,
            )
        with col_b:
            if st.button("📄 Export as PDF", use_container_width=True):
                path = export_pdf(data)
                with open(path, "rb") as f:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=f,
                        file_name=f"{data['student_name']}_roadmap.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )


if __name__ == "__main__":
    main()
