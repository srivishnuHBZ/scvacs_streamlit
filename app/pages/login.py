import streamlit as st
from app.utils.session import set_logged_in
import time
def render_page():
    # Check the current theme
    # theme = st.get_option("theme.base")
  
    # # Display the appropriate image based on the theme
    # if theme == "dark":
    #     st.markdown(
    #         "<img src='https://www.ums.edu.my/v5/images/2020/icon/LOGO_UMS_putih.png' width='500' style='display: block; margin: 0 auto;'>", 
    #         unsafe_allow_html=True
    #     )
    # else:
    #     st.markdown(
    #         "<img src='https://www.ums.edu.my/v5/images/icon/logo-umsblack-text-png.png' width='500' style='display: block; margin: 0 auto;'>", 
    #         unsafe_allow_html=True
    #     )
    st.markdown("<img src='https://seeklogo.com/images/U/Universiti_Malaysia_Sabah-logo-590ACB05AA-seeklogo.com.png' width='250' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Login to Smart Campus Vehicle Access Control System</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    if st.button("Login"):
        if username == "ramesh" and password == "ramesh@123": 
            set_logged_in()  # Update session state
            st.success("Login successful! Redirecting...")
            st.rerun()  # Reload the app to reflect logged-in state
            
        else:
            st.error("Invalid username or password.")

