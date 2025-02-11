# pages/2_Rep_Management.py
import streamlit as st
from database import init_db, fetch_all_reps, insert_rep, delete_rep

def display_header():
    logo_url = st.secrets["general"]["LOGO_URL"]
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(logo_url, width=80)
    with col2:
        st.markdown("<h1>Explore Results</h1>", unsafe_allow_html=True)

def app():
    st.title("Rep Management")
    st.write("Add or remove Reps, and define their team (DME or Ortho).")
    init_db()
    display_header()
    st.write("Exploring results...")
    # Form to add a new Rep
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
                st.write(f"{created_at}")
            with col3:
                if st.button(f"Delete {rep_name}", key=f"del_{rep_id}"):
                    delete_rep(rep_id)
                    st.warning(f"Deleted rep '{rep_name}'.")
                    st.experimental_rerun()

def main():
    app()

if __name__ == "__main__":
    main()
