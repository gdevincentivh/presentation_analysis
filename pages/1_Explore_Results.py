# pages/1_Explore_Results.py
import streamlit as st
import json
from datetime import date
from database import fetch_all_results, delete_analysis_record

def explore_login_flow():
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

    # Convert DB rows to a list of dicts
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

    filtered_data = data
    if selected_rep != "All":
        filtered_data = [d for d in filtered_data if d["Rep"] == selected_rep]
    if selected_team != "All":
        filtered_data = [d for d in filtered_data if d["Team"] == selected_team]
    filtered_data = [d for d in filtered_data if d["Demo Date"] and from_date <= d["Demo Date"] <= to_date]

    st.write(f"Showing {len(filtered_data)} record(s):")
    for record in filtered_data:
        with st.expander(f"Record #{record['ID']}: {record['Rep']} - {record['Team']}"):
            st.write(f"**Customer**: {record['Customer']}")
            st.write(f"**Demo Date**: {record['Demo Date']}")
            st.write(f"**Created At**: {record['Created At']}")
            st.json(record["Analysis"])

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
