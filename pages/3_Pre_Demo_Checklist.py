# pages/3_PreDemoChecklist.py
import streamlit as st

def app():
    st.title("Pre-Demo Checklist")
    st.markdown("Use this page to review your pre-demo questions.")

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

def main():
    app()

if __name__ == "__main__":
    main()
