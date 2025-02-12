# Home.py
import streamlit as st
import openai
import json
from datetime import datetime

from database import init_db, fetch_all_reps, get_rep_team, insert_demo_result

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
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=1500
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

def display_analysis(analysis: dict):
    st.header("Analysis Preview")
    # Show a partial overview or leave it minimal.
    scores = analysis.get("scores", {})
    if scores:
        st.subheader("Scores")
        for k, v in scores.items():
            st.write(f"- **{k.title()}**: {v}")

def main():
    st.set_page_config(
        page_title="Demo Analysis Tool",
        page_icon=st.secrets["general"]["FAVICON_URL"],
        layout="wide"
    )
    init_db()

    with st.sidebar:
        # Logo
        logo_url = st.secrets["general"]["LOGO_URL"]
        st.image(logo_url, use_container_width=True)

        st.title("Demo Information")
        reps_list = fetch_all_reps()  # (id, rep_name, team, created_at)
        rep_names = [r[1] for r in reps_list]

        if not rep_names:
            st.warning("No reps found! Please add them in 'Rep Management'.")
            rep_name = ""
        else:
            rep_name = st.selectbox("Rep Name", rep_names)

        customer_name = st.text_input("Customer")
        demo_date = st.date_input("Demo Date")

    st.title("Demo Analysis Tool")

    st.header("Demo Transcript")
    transcript = st.text_area("Paste transcript here:", height=200)

    if "gpt_analysis" not in st.session_state:
        st.session_state["gpt_analysis"] = None

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
                    display_analysis(analysis)

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
