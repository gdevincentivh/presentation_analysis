# pages/1_Explore_Results.py
import streamlit as st
import json
from datetime import date
from database import fetch_all_results

# Must be top line:
st.set_page_config(
    page_title="Explore Results",
    page_icon=":mag:",
    layout="wide"
)

def login_flow():
    st.subheader("Enter Password to View Results")
    with st.form("password_form"):
        password_input = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            correct_password = st.secrets["general"]["EXPLORE_PASSWORD"]
            if password_input == correct_password:
                st.session_state["auth"] = True
                st.stop()
            else:
                st.error("Invalid password. Try again.")
                st.stop()
                
def display_header():
    logo_url = st.secrets["general"]["LOGO_URL"]
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(logo_url, width=80)
    with col2:
        st.markdown("<h1>Explore Results</h1>", unsafe_allow_html=True)

def show_scores(scores: dict):
    st.markdown("**Scores**:")
    for cat, val in scores.items():
        st.write(f"- **{cat.title()}**: {val}/5")

def show_list_section(title: str, section_data: dict):
    # A helper to show bullet points
    st.markdown(f"**{title}**:")
    for area, bullet_points in section_data.items():
        st.write(f"**{area.title()}**")
        for bullet in bullet_points:
            st.markdown(f"- {bullet}")

def show_data():
    st.title("Explore Demo Results")

    rows = fetch_all_results()  # (id, rep_name, rep_team, customer_name, demo_date, analysis_json, created_at)
    if not rows:
        st.info("No demo results found yet.")
        return

    # Logout button
    if st.button("Logout"):
        st.session_state["auth"] = False
        st.stop()

    # Build a list of dicts for easier filtering
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
            "Demo Date": demo_date,       # e.g. "2025-02-11"
            "Created At": created_at,     # timestamp
            "Analysis": analysis_json
        })

    # =========== Filters ===========
    reps = sorted({d["Rep"] for d in data})
    selected_rep = st.selectbox("Filter by Rep", ["All"] + list(reps))

    teams = sorted({d["Team"] for d in data})
    selected_team = st.selectbox("Filter by Team", ["All"] + list(teams))

    # Date range filter: we find min/max from data
    all_dates = [d["Demo Date"] for d in data if d["Demo Date"]]
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
    else:
        min_date = date(2020, 1, 1)
        max_date = date.today()

    st.write("**Date Range Filter**")
    from_date = st.date_input("From Date", value=min_date)
    to_date = st.date_input("To Date", value=max_date)
    if from_date > to_date:
        st.error("From date cannot be greater than To date.")
        return

    # =========== Apply Filters ===========
    filtered_data = data
    if selected_rep != "All":
        filtered_data = [d for d in filtered_data if d["Rep"] == selected_rep]
    if selected_team != "All":
        filtered_data = [d for d in filtered_data if d["Team"] == selected_team]

    filtered_data = [d for d in filtered_data if d["Demo Date"] is not None and from_date <= d["Demo Date"] <= to_date]

    st.write(f"Showing {len(filtered_data)} record(s):")
    for row in filtered_data:
        with st.expander(f"Record #{row['ID']}: {row['Rep']} - {row['Team']}"):
            st.write(f"**Customer**: {row['Customer']}")
            st.write(f"**Demo Date**: {row['Demo Date']}")
            st.write(f"**Created At**: {row['Created At']}")

            analysis = row["Analysis"]
            # Show Scores
            scores = analysis.get("scores", {})
            if scores:
                show_scores(scores)

            # Show Strengths
            strengths = analysis.get("strengths", {})
            if strengths:
                show_list_section("Strengths", strengths)

            # Show Improvements
            improvements = analysis.get("improvements", {})
            if improvements:
                show_list_section("Improvements", improvements)

            # ... Similarly, you can parse out other sections or
            # show them in a style you prefer.

def app():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False

    if not st.session_state["auth"]:
        login_flow()
    else:
        show_data()
    display_header()
    st.write("Exploring results...")

def main():
    app()

if __name__ == "__main__":
    main()