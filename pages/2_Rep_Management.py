# pages/2_Rep_Management.py
import streamlit as st
from database import init_db, fetch_all_reps, insert_rep, delete_rep

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

def show_rep_management():
    st.title("Rep Management")
    st.write("Add or remove reps, and define their team (DME or Ortho).")

    init_db()

    with st.form("add_rep_form"):
        rep_name_input = st.text_input("Rep Name")
        team_input = st.selectbox("Team", ["DME", "Ortho"])
        submitted = st.form_submit_button("Add/Update Rep")
        if submitted:
            if rep_name_input.strip():
                insert_rep(rep_name_input.strip(), team_input)
                st.success(f"Added/Updated rep '{rep_name_input}' as {team_input}.")
            else:
                st.error("Rep name cannot be empty.")

    st.subheader("Current Reps")
    rep_rows = fetch_all_reps()
    if not rep_rows:
        st.info("No reps in the system.")
    else:
        for (rep_id, rep_name, team, created_at) in rep_rows:
            col1, col2, col3 = st.columns([3,2,2])
            with col1:
                st.write(f"**{rep_name}** - {team}")
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
