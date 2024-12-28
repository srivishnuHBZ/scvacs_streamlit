import streamlit as st
from app.utils.session import set_logged_in
import os
import base64

def render_page():
    # Get the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "ums_logo.png")
    
    # Read and encode the image
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
        encoded_image = base64.b64encode(img_bytes).decode()
    
    # Display centered image using markdown
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <img src='data:image/png;base64,{encoded_image}' width='250'/>
        </div>
        """,
        unsafe_allow_html=True
    )
    
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

