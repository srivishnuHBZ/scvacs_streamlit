import streamlit as st
from app.utils.session import set_logged_in
import time
def render_page():
    st.markdown("<img src='https://seeklogo.com/images/U/Universiti_Malaysia_Sabah-logo-590ACB05AA-seeklogo.com.png' width='250' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Login to Smart Campus Vehicle Access Control System</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    if st.button("Login"):
        if username == "" and password == "": 
            set_logged_in()  # Update session state
            st.success("Login successful! Redirecting...")
            st.rerun()  # Reload the app to reflect logged-in state
            
        else:
            st.error("Invalid username or password.")

