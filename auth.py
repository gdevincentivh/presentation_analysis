# auth.py
import streamlit as st

def require_global_auth():
    """
    If user is not authenticated, show a password form.
    If user enters the correct password, set st.session_state["global_auth"] = True.
    Otherwise, st.stop() to prevent showing the rest of the page.
    """
    if "global_auth" not in st.session_state:
        st.session_state["global_auth"] = False

    if not st.session_state["global_auth"]:
        # Show a simple login form
        st.title("Enter App Password")
        with st.form("global_app_form"):
            pwd = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                correct_pwd = st.secrets["general"]["GLOBAL_APP_PASSWORD"]
                if pwd == correct_pwd:
                    st.session_state["global_auth"] = True
                    st.stop()
                else:
                    st.error("Invalid password.")
        # We stop the script so no further code on this page runs
        st.stop()
