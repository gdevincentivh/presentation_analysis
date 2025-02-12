# pages/2_Rep_Management.py
import streamlit as st
from database import (
    init_db, fetch_all_reps, insert_rep, delete_rep,
    fetch_all_teams, insert_team, delete_team
)

def rep_mgmt_login_flow():
    st.subheader("Enter Password for Rep Management")
    with st.form("rep_mgmt_form"):
        pwd_input = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Submit")
        if submitted:
            correct_pwd = st.secrets["general"]["REP_MANAGEMENT_PASSWORD"]
            if pwd_input == correct_pwd:
                st.session_state["rep_mgr_auth"] = True
                st.stop()
            else:
                st.error("Invalid password. Please try again.")

def show_team_management():
    st.subheader("Team Management")

    # Create new team
    with st.form("add_team_form"):
        new_team = st.text_input("New Team Name")
        submitted = st.form_submit_button("Add Team")
        if submitted:
            if new_team.strip():
                insert_team(new_team.strip())
                st.success(f"Team '{new_team}' added.")
            else:
                st.error("Team name cannot be empty.")

    # Display existing teams
    teams = fetch_all_teams()  # (id, team_name, created_at)
    if not teams:
        st.info("No teams found.")
    else:
        st.write("**Existing Teams**")
        for (team_id, team_name, created_at) in teams:
            col1, col2 = st.columns([3,1])
            with col1:
                st.write(f"**{team_name}** (added {created_at})")
            with col2:
                if st.button(f"Delete {team_name}", key=f"teamdel_{team_id}"):
                    delete_team(team_id)
                    st.warning(f"Deleted team '{team_name}'.")
                    st.stop()

def show_rep_management():
    st.title("Rep Management")
    st.write("Add or remove reps, and define their team from a dynamic list.")

    init_db()

    # 1) Team Management Section
    show_team_management()

    st.subheader("Add/Update a Rep")
    # 2) Display a selectbox of available teams
    teams_data = fetch_all_teams()  # (id, team_name, created_at)
    team_names = [t[1] for t in teams_data]

    with st.form("add_rep_form"):
        rep_name_input = st.text_input("Rep Name")
        chosen_team = ""
        if team_names:
            chosen_team = st.selectbox("Select Team", team_names)
        else:
            st.warning("No teams found. Create a team first.")
        submitted = st.form_submit_button("Add Rep")
        if submitted:
            if not rep_name_input.strip():
                st.error("Rep name cannot be empty.")
            elif not chosen_team:
                st.error("Please select a valid team.")
            else:
                insert_rep(rep_name_input.strip(), chosen_team)
                st.success(f"Added/Updated rep '{rep_name_input}' on team '{chosen_team}'.")

    st.subheader("Current Reps")
    rep_rows = fetch_all_reps()
    if not rep_rows:
        st.info("No reps in the system.")
    else:
        for (rep_id, rep_name, team, created_at) in rep_rows:
            col1, col2, col3 = st.columns([3,2,2])
            with col1:
                st.write(f"**{rep_name}** - Team: {team}")
            with col2:
                st.write(str(created_at))
            with col3:
                if st.button(f"Delete {rep_name}", key=f"del_{rep_id}"):
                    delete_rep(rep_id)
                    st.warning(f"Deleted rep '{rep_name}'.")
                    st.stop()

def app():
    if "rep_mgr_auth" not in st.session_state:
        st.session_state["rep_mgr_auth"] = False

    if not st.session_state["rep_mgr_auth"]:
        rep_mgmt_login_flow()
    else:
        if st.button("Logout (Rep Management)"):
            st.session_state["rep_mgr_auth"] = False
            st.stop()
        show_rep_management()

def main():
    app()

if __name__ == "__main__":
    main()
