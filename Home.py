# Home.py
import streamlit as st
import openai
import json
from datetime import datetime

from database import init_db, fetch_all_reps, get_rep_team, insert_demo_result

#####################
# HELPER FUNCTIONS
#####################

def bullet_list(items):
    """Displays each string in 'items' as a bullet."""
    for i in items:
        st.markdown(f"- {i}")

def show_scores(scores: dict):
    """Display the 'scores' section in bullet style."""
    if not scores:
        return
    st.subheader("Scores")
    for cat, val in scores.items():
        st.write(f"**{cat.title()}**: {val}/5")

def show_section(title: str, section_data: dict):
    """
    For sections like 'strengths', 'improvements', 'examples' that map area_name -> [bullets].
    """
    if not section_data:
        return
    st.subheader(title)
    for area, bullets in section_data.items():
        st.markdown(f"**{area.replace('_',' ').title()}**")
        bullet_list(bullets)

def show_pain_points(pain_points: dict):
    """
    'pain_points': {
      "operational": [...],
      "technical": [...],
      "financial": [...],
      "priority_level": { "some pain text":"High/Medium/Low" }
    }
    """
    if not pain_points:
        return
    st.subheader("Pain Points")
    for category in ["operational", "technical", "financial"]:
        points = pain_points.get(category, [])
        if points:
            st.markdown(f"**{category.title()}**")
            bullet_list(points)
    priority_map = pain_points.get("priority_level", {})
    if priority_map:
        st.markdown("**Priority Levels**")
        for key, level in priority_map.items():
            st.write(f"- **{key}**: {level}")

def show_buying_signals(buying_signals: dict):
    """
    'buying_signals': {"positive": [...], "concerns": [...]}
    """
    if not buying_signals:
        return
    st.subheader("Buying Signals")
    positives = buying_signals.get("positive", [])
    if positives:
        st.markdown("**Positive**")
        bullet_list(positives)
    concerns = buying_signals.get("concerns", [])
    if concerns:
        st.markdown("**Concerns**")
        bullet_list(concerns)

def show_next_steps(steps: list):
    """
    next_steps: [
      {"action":"...", "owner":"...", "deadline":"...", "priority":"High/Medium/Low"}
    ]
    """
    if not steps:
        return
    st.subheader("Next Steps")
    for i, step in enumerate(steps, start=1):
        action = step.get("action","")
        owner = step.get("owner","")
        deadline = step.get("deadline","")
        priority = step.get("priority","")
        st.markdown(f"**Step {i}**")
        st.write(f"- **Action**: {action}")
        st.write(f"- **Owner**: {owner}")
        st.write(f"- **Deadline**: {deadline}")
        st.write(f"- **Priority**: {priority}")

def show_management_summary(summary: dict):
    """
    'management_summary': { "key_points": [...], "decisions": [...], "risks": [...], "recommendations": [...] }
    """
    if not summary:
        return
    st.subheader("Management Summary")
    if "key_points" in summary:
        st.markdown("**Key Points**")
        bullet_list(summary["key_points"])
    if "decisions" in summary:
        st.markdown("**Decisions**")
        bullet_list(summary["decisions"])
    if "risks" in summary:
        st.markdown("**Risks**")
        bullet_list(summary["risks"])
    if "recommendations" in summary:
        st.markdown("**Recommendations**")
        bullet_list(summary["recommendations"])


def show_analysis_pretty(analysis: dict):
    """
    Display the entire GPT analysis in a "cool", bullet-based style.
    """
    # 1) Scores
    show_scores(analysis.get("scores", {}))
    # 2) Strengths
    show_section("Strengths", analysis.get("strengths", {}))
    # 3) Improvements
    show_section("Improvements", analysis.get("improvements", {}))
    # 4) Examples
    show_section("Examples", analysis.get("examples", {}))
    # 5) Pain Points
    show_pain_points(analysis.get("pain_points", {}))
    # 6) Buying Signals
    show_buying_signals(analysis.get("buying_signals", {}))
    # 7) Next Steps
    show_next_steps(analysis.get("next_steps", []))
    # 8) Management Summary
    show_management_summary(analysis.get("management_summary", {}))

#####################
# DEMO ANALYZER
#####################

class DemoAnalyzer:
    def __init__(self):
        openai.api_key = st.secrets["general"]["OPENAI_API_KEY"]

    def analyze_demo_performance(self, transcript: str) -> dict:
        response_text = ""
        try:
            system_prompt = (
                "You are an expert sales coach analyzing demo performance. "
                "Return ONLY a valid JSON object with no additional text."
            )
            user_prompt = f"""
Analyze this transcript and return JSON with:
{{
  "scores": {{ "discovery":1-5, "value_proposition":1-5, "technical_clarity":1-5,
               "objection_handling":1-5, "demo_flow":1-5, "next_steps":1-5 }},
  "strengths": {{ "area_name": ["points"] }},
  "improvements": {{ "area_name": ["points"] }},
  "examples": {{ "area_name": ["examples"] }},
  "pain_points": {{
      "operational": ["issues"], "technical": ["issues"], "financial": ["issues"],
      "priority_level": {{"pain_point":"High/Medium/Low"}}
  }},
  "buying_signals": {{ "positive":["signals"], "concerns":["concerns"] }},
  "next_steps": [
    {{ "action":"", "owner":"", "deadline":"", "priority":"High/Medium/Low" }}
  ],
  "management_summary": {{
    "key_points":["points"], "decisions":["decisions"],
    "risks":["risks"], "recommendations":["recommendations"]
  }}
}}
TRANSCRIPT:
{transcript}
"""
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=15000
            )
            response_text = response.choices[0].message.content.strip()

            # Attempt direct JSON parse
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx == -1 or end_idx <= start_idx:
                    raise ValueError("No valid JSON found in GPT response.")
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)

        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            if response_text:
                st.error(f"Raw GPT response: {response_text[:500]}...")
            return {}

#####################
# MAIN
#####################

def main():
    st.set_page_config(
        page_title="Presentation Analysis Tool",
        page_icon=st.secrets["general"]["FAVICON_URL"],
        layout="wide"
    )
    from database import init_db, fetch_all_reps, get_rep_team, insert_demo_result
    init_db()

    # Sidebar with logo & user input
    with st.sidebar:
        logo_url = st.secrets["general"]["LOGO_URL"]
        st.image(logo_url, use_container_width=True)

        st.title("Prensentation Information")
        reps_list = fetch_all_reps()
        rep_names = [r[1] for r in reps_list]
        if not rep_names:
            st.warning("No reps found! Please add them in 'Rep Management'.")
            rep_name = ""
        else:
            rep_name = st.selectbox("Rep Name", rep_names)

        customer_name = st.text_input("Customer")
        demo_date = st.date_input("Demo Date")

    st.title("Demo Analysis Tool")

    # Transcript Input
    st.header("Demo Transcript")
    transcript = st.text_area("Paste transcript here:", height=200)

    if "gpt_analysis" not in st.session_state:
        st.session_state["gpt_analysis"] = None

    # Step 1: Analyze
    if st.button("Analyze Demo"):
        if not transcript.strip():
            st.error("Please paste a transcript.")
        elif not rep_name:
            st.error("No Rep selected.")
        else:
            with st.spinner("Analyzing..."):
                analyzer = DemoAnalyzer()
                analysis = analyzer.analyze_demo_performance(transcript)
                st.session_state["gpt_analysis"] = analysis
                if analysis:
                    # Show the full bullet-style analysis right away
                    show_analysis_pretty(analysis)

    # Step 2: Confirm & Send
    if st.button("Confirm & Send to DB"):
        analysis = st.session_state["gpt_analysis"]
        if not analysis:
            st.error("No analysis to save. Run 'Analyze Demo' first.")
        else:
            rep_team = get_rep_team(rep_name) or "Unknown"
            insert_demo_result(
                rep_name=rep_name,
                rep_team=rep_team,
                customer_name=customer_name,
                demo_date=str(demo_date),
                analysis_json=json.dumps(analysis)
            )
            st.success(f"Saved record for Rep: {rep_name} (Team: {rep_team}).")
            st.session_state["gpt_analysis"] = None

if __name__ == "__main__":
    main()
