import streamlit as st

def set_logged_in():
    st.session_state["logged_in"] = True

def is_logged_in():
    return st.session_state.get("logged_in", False)
