# Prompt Design Documentation

## Goal
Get the Gemini model to reliably produce a **personalized, high-quality, and correctly-structured** learning roadmap — every time, without manual JSON cleanup or retries.

## Two-part prompt strategy

### 1. System Instruction (fixed, sent every time)
Defines the model's **role** and **rules**, independent of any specific student:

- Role: "expert career mentor and curriculum designer with 15+ years of experience"
  → Framing the model as a domain expert measurably improves depth and relevance of advice compared to a generic assistant framing.
- Explicit rules against:
  - Assuming skills the student didn't mention
  - Ignoring the student's stated daily study hours
  - Recommending resources that don't really exist (hallucination guard)
  - Generic, non-actionable career tips
- Explicit output rule: **"Respond ONLY with valid JSON... no commentary, no markdown"**
  → Even though we also enforce a schema at the API level, repeating this in-prompt reduces the chance of the model wrapping JSON in ```json fences or adding preamble text.

### 2. User Prompt (built per-request)
Injects the actual student data (name, skills, goal, hours) into a template that also **restates quantity/structure expectations** for each field, e.g.:
- "3-5 phases" for the roadmap
- "at least the first 4-6 weeks" for the weekly plan
- "5-10 skills, ordered by priority"

This prevents the model from being too sparse (e.g., returning only 1 phase or 2 resources) — a common failure mode when quantity isn't specified.

## Structured Output Enforcement

Rather than relying purely on prompt instructions (which can fail), we use Gemini's native **`response_schema`** + **`response_mime_type: "application/json"`** generation config. This:

- Guarantees the response is syntactically valid JSON
- Guarantees all required top-level fields are present
- Removes the need for regex/manual cleanup of the model's output
- Lets the app safely call `json.loads(response.text)` directly

The schema (`ROADMAP_SCHEMA` in `app.py`) mirrors the assignment's required sections exactly:
`learning_roadmap`, `weekly_study_plan`, `recommended_skills`, `suggested_projects`, `learning_resources`, `career_tips` — plus `student_name`, `career_goal`, and `overview` for a friendly summary.

## Design decisions & trade-offs

| Decision | Reasoning |
|---|---|
| `temperature: 0.7` | Balances creativity (varied project ideas, phrasing) with consistency (still follows schema/rules reliably). Lower would feel robotic; higher risks inconsistent quality. |
| Nested objects instead of flat strings (e.g. `learning_roadmap` as array of `{phase, duration, focus_area, milestones}`) | Keeps the UI able to render structured tabs/expanders instead of parsing free text. |
| Explicit "do not invent fake resources" rule | LLMs are prone to hallucinating course names/links. This rule (plus asking for "well-known" resources) reduces — though doesn't fully eliminate — that risk. Users should still verify links independently. |
| Separate `overview` field | Gives a short, friendly one-paragraph summary for the top of the results page, improving UX without cluttering the structured sections. |

## Known limitations

- The model can still occasionally suggest a resource that's outdated or a link that doesn't exist (verify before relying on it).
- Very unusual career goals (e.g., extremely niche fields) may produce a lower-quality roadmap since the model has less training data to draw from.
- The weekly plan currently caps at "first 4-6 weeks" rather than a full multi-month week-by-week breakdown, to keep response size and generation time reasonable.
