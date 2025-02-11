import streamlit as st
import json
from datetime import date
from database import fetch_all_results, delete_analysis_record

#####################
# HELPER FUNCTIONS
#####################

def explore_login_flow():
    """
    Two possible passwords:
      - EXPLORE_PASSWORD (read-only)
      - SUPERADMIN_PASSWORD (can delete)
    """
    st.subheader("Enter Password to View Results")
    with st.form("explore_form"):
        password_input = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Submit")
        if submitted:
            reg_pass = st.secrets["general"]["EXPLORE_PASSWORD"]
            admin_pass = st.secrets["general"]["SUPERADMIN_PASSWORD"]

            if password_input == admin_pass:
                st.session_state["explore_auth"] = True
                st.session_state["role"] = "superadmin"
                st.stop()
            elif password_input == reg_pass:
                st.session_state["explore_auth"] = True
                st.session_state["role"] = "user"
                st.stop()
            else:
                st.error("Invalid password!")

def bullet_list(items):
    """
    Given a list of strings, show each as a bullet point.
    """
    for i in items:
        st.markdown(f"- {i}")

def show_scores(scores: dict):
    """
    Show the 'scores' section in a friendlier bullet style.
    """
    if not scores:
        return
    st.subheader("Scores")
    for cat, val in scores.items():
        st.write(f"**{cat.title()}**: {val}/5")

def show_strengths(strengths: dict):
    """
    Show 'strengths' section: keys are area names, values are lists of bullet points.
    """
    if not strengths:
        return
    st.subheader("Strengths")
    for area_name, bullet_points in strengths.items():
        st.markdown(f"**{area_name.replace('_',' ').title()}**")
        bullet_list(bullet_points)

def show_improvements(improvements: dict):
    """
    Similar to strengths but for 'improvements'.
    """
    if not improvements:
        return
    st.subheader("Improvements")
    for area_name, bullet_points in improvements.items():
        st.markdown(f"**{area_name.replace('_',' ').title()}**")
        bullet_list(bullet_points)

def show_examples(examples: dict):
    """
    Similar approach for 'examples'.
    """
    if not examples:
        return
    st.subheader("Examples")
    for area_name, bullet_points in examples.items():
        st.markdown(f"**{area_name.replace('_',' ').title()}**")
        bullet_list(bullet_points)

def show_pain_points(pain_points: dict):
    """
    'pain_points': {
        "operational": [...],
        "technical": [...],
        "financial": [...],
        "priority_level": { "pain_point": "High/Medium/Low" }
    }
    We'll show bullet points for each category, then show the 'priority_level' mapping if present.
    """
    if not pain_points:
        return
    st.subheader("Pain Points")

    # We'll handle "operational", "technical", "financial"
    for category in ["operational", "technical", "financial"]:
        points = pain_points.get(category, [])
        if points:
            st.markdown(f"**{category.title()}**")
            bullet_list(points)

    priority_map = pain_points.get("priority_level", {})
    if priority_map:
        st.markdown("**Priority Levels**")
        # e.g. { "some pain text": "High", ... }
        for pain, level in priority_map.items():
            st.write(f"- **{pain}**: {level}")

def show_buying_signals(buying_signals: dict):
    """
    'buying_signals': {
        "positive": [...],
        "concerns": [...]
    }
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
    Each step is a dict with {action, owner, deadline, priority}
    """
    if not steps:
        return
    st.subheader("Next Steps")
    for idx, step in enumerate(steps, start=1):
        action = step.get("action", "")
        owner = step.get("owner", "")
        deadline = step.get("deadline", "")
        priority = step.get("priority", "")
        st.markdown(f"**Step {idx}**")
        st.write(f"- **Action**: {action}")
        st.write(f"- **Owner**: {owner}")
        st.write(f"- **Deadline**: {deadline}")
        st.write(f"- **Priority**: {priority}")

def show_management_summary(summary: dict):
    """
    'management_summary': {
      "key_points": [...],
      "decisions": [...],
      "risks": [...],
      "recommendations": [...]
    }
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
    Main function to display the entire analysis in a "cool" bullet style,
    rather than raw JSON.
    """
    # 1) Scores
    show_scores(analysis.get("scores", {}))

    # 2) Strengths
    show_strengths(analysis.get("strengths", {}))

    # 3) Improvements
    show_improvements(analysis.get("improvements", {}))

    # 4) Examples
    show_examples(analysis.get("examples", {}))

    # 5) Pain Points
    show_pain_points(analysis.get("pain_points", {}))

    # 6) Buying Signals
    show_buying_signals(analysis.get("buying_signals", {}))

    # 7) Next Steps
    show_next_steps(analysis.get("next_steps", []))

    # 8) Management Summary
    show_management_summary(analysis.get("management_summary", {}))

#####################
# MAIN PAGE LOGIC
#####################

def show_data():
    st.title("Explore Demo Results")

    current_role = st.session_state.get("role", "user")
    rows = fetch_all_results()
    if not rows:
        st.info("No demo results found.")
        return

    if st.button("Logout"):
        st.session_state["explore_auth"] = False
        st.session_state["role"] = "user"
        st.stop()

    # Build data structure
    data = []
    for (id_val, rep_name, rep_team, customer_name, demo_date, analysis_str, created_at) in rows:
        try:
            analysis_json = json.loads(analysis_str)
        except json.JSONDecodeError:
            analysis_json = {}
        data.append({
            "ID": id_val,
            "Rep": rep_name,
            "Team": rep_team,
            "Customer": customer_name,
            "Demo Date": demo_date,
            "Created At": created_at,
            "Analysis": analysis_json
        })

    # =========== Filters ===========
    reps = sorted({d["Rep"] for d in data})
    selected_rep = st.selectbox("Filter by Rep", ["All"] + list(reps))

    teams = sorted({d["Team"] for d in data})
    selected_team = st.selectbox("Filter by Team", ["All"] + list(teams))

    all_dates = [d["Demo Date"] for d in data if d["Demo Date"]]
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
    else:
        min_date = date(2020, 1, 1)
        max_date = date.today()

    st.markdown("### Date Range Filter")
    from_date = st.date_input("From Date", value=min_date)
    to_date = st.date_input("To Date", value=max_date)
    if from_date > to_date:
        st.error("From Date cannot exceed To Date.")
        return

    # Filter logic
    filtered_data = data
    if selected_rep != "All":
        filtered_data = [d for d in filtered_data if d["Rep"] == selected_rep]
    if selected_team != "All":
        filtered_data = [d for d in filtered_data if d["Team"] == selected_team]
    filtered_data = [d for d in filtered_data if d["Demo Date"] and from_date <= d["Demo Date"] <= to_date]

    st.write(f"Showing {len(filtered_data)} record(s):")

    # Show each record in an expander
    for record in filtered_data:
        with st.expander(f"Record #{record['ID']}: {record['Rep']} - {record['Team']}"):
            st.write(f"**Customer**: {record['Customer']}")
            st.write(f"**Demo Date**: {record['Demo Date']}")
            st.write(f"**Created At**: {record['Created At']}")
            
            # Show the bullet-style analysis
            show_analysis_pretty(record["Analysis"])

            # Optionally show raw JSON if user checks
            show_raw = st.checkbox("Show Raw JSON", key=f"raw_{record['ID']}")
            if show_raw:
                st.json(record["Analysis"])

            # If superadmin, show delete button
            if current_role == "superadmin":
                if st.button(f"Delete #{record['ID']}", key=f"del_{record['ID']}"):
                    delete_analysis_record(record['ID'])
                    st.warning(f"Deleted record #{record['ID']}.")
                    st.stop()

def app():
    if "explore_auth" not in st.session_state:
        st.session_state["explore_auth"] = False
    if "role" not in st.session_state:
        st.session_state["role"] = "user"

    if not st.session_state["explore_auth"]:
        explore_login_flow()
    else:
        show_data()

def main():
    app()

if __name__ == "__main__":
    main()
