# app.py
import streamlit as st
import openai
import json
from datetime import datetime

from database import init_db, fetch_all_reps, get_rep_team, insert_demo_result

st.set_page_config(
        page_title="Demo Analysis Tool",
        page_icon=st.secrets["general"]["FAVICON_URL"],  # from secrets
        layout="wide"
    )



# -------------------------------------------
# 2. DemoAnalyzer Class
# -------------------------------------------
class DemoAnalyzer:
    def __init__(self):
        api_key = st.secrets["general"]["OPENAI_API_KEY"]
        openai.api_key = api_key

    def analyze_demo_performance(self, transcript: str) -> dict:
        response_text = ""
        try:
            system_prompt = (
                "You are an expert sales coach analyzing demo performance. "
                "Return ONLY a valid JSON object with no additional text."
            )
            
            # The official fields
            user_prompt = f"""
Analyze this demo transcript and return a JSON object with exactly these fields:

{{
    "scores": {{
        "discovery": 1-5,
        "value_proposition": 1-5,
        "technical_clarity": 1-5,
        "objection_handling": 1-5,
        "demo_flow": 1-5,
        "next_steps": 1-5
    }},
    "strengths": {{
        "area_name": ["specific strength points"]
    }},
    "improvements": {{
        "area_name": ["specific improvement points"]
    }},
    "examples": {{
        "area_name": ["specific transcript examples"]
    }},
    "pain_points": {{
        "operational": ["list of operational challenges"],
        "technical": ["list of technical challenges"],
        "financial": ["list of financial concerns"],
        "priority_level": {{
            "pain_point": "High/Medium/Low"
        }}
    }},
    "buying_signals": {{
        "positive": ["list of positive signals"],
        "concerns": ["list of concerns/objections"]
    }},
    "next_steps": [
        {{
            "action": "specific task",
            "owner": "responsible party",
            "deadline": "timeframe",
            "priority": "High/Medium/Low"
        }}
    ],
    "management_summary": {{
        "key_points": ["list of key discussion points"],
        "decisions": ["list of decisions made"],
        "risks": ["identified risks"],
        "recommendations": ["key recommendations"]
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
                max_tokens=1500
            )

            response_text = response.choices[0].message.content.strip()

            # Try parse JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx == -1 or end_idx <= start_idx:
                    raise ValueError("No valid JSON object found in response.")
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)

        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            if response_text:
                st.error(f"Raw response: {response_text[:500]}...")
            return {}

# -------------------------------------------
# 3. PreDemoChecklist
# -------------------------------------------
class PreDemoChecklist:
    @staticmethod
    def display():
        with st.expander("📋 Pre-Demo Checklist", expanded=True):
            st.markdown("### Questions to Cover")
            cols = st.columns(2)
            with cols[0]:
                st.markdown("#### Organization")
                st.checkbox("Organization type (Hospital/Practice/FQHC)")
                st.checkbox("Primary specialty/focus areas")
                st.checkbox("Number of locations/providers")
                st.checkbox("Current challenges/pain points")
                st.checkbox("Decision-making structure")
                st.checkbox("Implementation timeline")
                
                st.markdown("#### Patient Population")
                st.checkbox("Initial enrollment target")
                st.checkbox("Total patient pool size")
                st.checkbox("Insurance mix/coverage")
                st.checkbox("Target disease states")
                st.checkbox("Key demographics")
                
            with cols[1]:
                st.markdown("#### Technical Requirements")
                st.checkbox("Current EHR system/version")
                st.checkbox("Integration requirements")
                st.checkbox("Security/compliance needs")
                st.checkbox("Current digital health solutions")
                st.checkbox("Infrastructure constraints")
                st.checkbox("User workflow requirements")
                
                st.markdown("#### Financial/ROI")
                st.checkbox("Budget range/constraints")
                st.checkbox("ROI expectations")
                st.checkbox("Current billing processes")
                st.checkbox("Relevant CPT codes")
                st.checkbox("Value-based care initiatives")

# -------------------------------------------
# 4. Display Analysis
# -------------------------------------------
def display_analysis(analysis: dict):
    st.header("Demo Performance Analysis")
    
    # Management Summary
    with st.expander("📊 Management Summary", expanded=True):
        summary = analysis.get("management_summary", {})
        if summary:
            cols = st.columns(2)
            with cols[0]:
                st.markdown("### Key Points & Decisions")
                for point in summary.get("key_points", []):
                    st.markdown(f"• {point}")
                for decision in summary.get("decisions", []):
                    st.markdown(f"✓ {decision}")
                    
            with cols[1]:
                st.markdown("### Risks & Recommendations")
                for risk in summary.get("risks", []):
                    st.markdown(f"⚠️ {risk}")
                for rec in summary.get("recommendations", []):
                    st.markdown(f"💡 {rec}")

    # Overall Score
    scores = analysis.get("scores", {})
    if scores:
        numeric_scores = [v for v in scores.values() if isinstance(v, (int, float))]
        if numeric_scores:
            overall = sum(numeric_scores) / len(numeric_scores)
            st.metric("Overall Demo Score", f"{overall:.1f}/5.0")

    # Pain Points & Buying Signals
    cols = st.columns(2)
    with cols[0]:
        with st.expander("🎯 Pain Points", expanded=True):
            pain_points = analysis.get("pain_points", {})
            for category, points in pain_points.items():
                if category != "priority_level":
                    st.markdown(f"**{category.title()}**")
                    for point in points:
                        priority = pain_points.get("priority_level", {}).get(point, "Medium")
                        emoji = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
                        st.markdown(f"{emoji} {point}")
                            
    with cols[1]:
        with st.expander("💭 Buying Signals", expanded=True):
            buying_signals = analysis.get("buying_signals", {})
            positives = buying_signals.get("positive", [])
            concerns = buying_signals.get("concerns", [])
            
            st.markdown("**Positive Signals**")
            for signal in positives:
                st.markdown(f"✅ {signal}")
                
            st.markdown("**Concerns/Objections**")
            for concern in concerns:
                st.markdown(f"❓ {concern}")

    # Strengths, Improvements, Examples
    columns = st.columns(3)
    with columns[0]:
        with st.expander("💪 Strengths", expanded=True):
            strengths = analysis.get("strengths", {})
            for area, details in strengths.items():
                area_score = scores.get(area, 0)
                st.markdown(f"**{area}** ({area_score}/5)")
                for point in details:
                    st.markdown(f"• {point}")
    
    with columns[1]:
        with st.expander("🎯 Areas for Improvement", expanded=True):
            improvements = analysis.get("improvements", {})
            for area, details in improvements.items():
                area_score = scores.get(area, 0)
                st.markdown(f"**{area}** ({area_score}/5)")
                for point in details:
                    st.markdown(f"• {point}")

    with columns[2]:
        with st.expander("📝 Specific Examples", expanded=True):
            examples = analysis.get("examples", {})
            for area, ex_list in examples.items():
                st.markdown(f"**{area}**")
                for ex in ex_list:
                    st.markdown(f"• {ex}")

    # Next Steps
    with st.expander("📋 Next Steps", expanded=True):
        next_steps = analysis.get("next_steps", [])
        for item in next_steps:
            action = item.get("action", "")
            owner = item.get("owner", "")
            deadline = item.get("deadline", "")
            priority = item.get("priority", "")
            priority_emoji = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
            st.markdown(f"{priority_emoji} **{action}**")
            st.markdown(f"Owner: {owner} | Due: {deadline}")

# -------------------------------------------
# 5. Main Page
# -------------------------------------------

def main():
    # Initialize DB
    init_db()

    # Set custom favicon and page title
    
    # Load reps for dropdown
    reps_list = fetch_all_reps()  # each row = (id, rep_name, team, created_at)
    rep_names = [r[1] for r in reps_list]

    with st.sidebar:
        # Logo from secrets
        logo_url = st.secrets["general"]["LOGO_URL"]
        st.image(logo_url, use_container_width=True)
        
        st.header("Demo Information")
        if not rep_names:
            st.warning("No reps found. Please add reps in 'Rep Management' page.")
            rep_name = ""
        else:
            rep_name = st.selectbox("Rep Name", rep_names)
        
        customer_name = st.text_input("Customer")
        demo_date = st.date_input("Demo Date")
        
    st.title("Demo Analysis Tool")
    PreDemoChecklist.display()

    st.header("Demo Recording Analysis")
    transcript = st.text_area("Paste demo transcript:", height=200)

    # We'll store GPT analysis in session for two-step approach
    if "gpt_analysis" not in st.session_state:
        st.session_state["gpt_analysis"] = None

    # Step 1: Analyze
    if st.button("Analyze Demo"):
        if not transcript.strip():
            st.error("Please paste a demo transcript.")
        elif not rep_name and not rep_names:
            st.error("No Rep selected or available. Add a rep first.")
        else:
            with st.spinner("Analyzing..."):
                analyzer = DemoAnalyzer()
                analysis = analyzer.analyze_demo_performance(transcript)
                st.session_state["gpt_analysis"] = analysis
                if analysis:
                    display_analysis(analysis)

    # Step 2: Confirm & Send to DB
    if st.button("Confirm & Send to DB"):
        analysis = st.session_state.get("gpt_analysis")
        if not analysis:
            st.error("No analysis available. Please run 'Analyze Demo' first.")
        else:
            if not rep_name:
                st.error("Please select a valid rep.")
            else:
                # Get the team from the DB
                rep_team = get_rep_team(rep_name) or "Unknown"
                insert_demo_result(
                    rep_name=rep_name,
                    rep_team=rep_team,
                    customer_name=customer_name,
                    demo_date=str(demo_date),
                    analysis_json=json.dumps(analysis)
                )
                st.success(f"Demo analysis saved. Rep: {rep_name} (Team: {rep_team}).")
                st.session_state["gpt_analysis"] = None  # clear

if __name__ == "__main__":
    main()
