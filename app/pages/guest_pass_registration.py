import streamlit as st
from datetime import datetime, timedelta
from app.database import engine
from sqlalchemy import text
import re
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
from app.database import insert_guest, fetch_recent_registrations

def validate_phone_number(phone):
    pattern = re.compile(r'^\+?[1-9]\d{7,14}$')
    return bool(pattern.match(phone)) if phone else True

def validate_email(email):
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(pattern.match(email)) if email else True

def validate_plate_number(plate):
    pattern = re.compile(r'^[A-Za-z0-9]{1,10}$')
    return bool(pattern.match(plate))


def render_page():
        
    st.title("Guest Pass Registration")

    # Initialize session state
    if 'show_success' not in st.session_state:
        st.session_state.show_success = False
    if 'success_time' not in st.session_state:
        st.session_state.success_time = None

    # Split the screen into two columns
    col1, col2 = st.columns([1, 1])

    # Left column - Registration Form
    with col1:
        st.subheader("Registration Form")

        # Handle success message with auto-disappear
        message_placeholder = st.empty()
        if st.session_state.show_success:
            message_placeholder.success("Guest registration successful!")
            # Check if it's time to hide the message (after 3 seconds)
            if st.session_state.success_time and time.time() - st.session_state.success_time > 3:
                st.session_state.show_success = False
                st.session_state.success_time = None
                message_placeholder.empty()
        else:
            message_placeholder.empty()  # Ensure placeholder is cleared

        with st.form("guest_registration_form", clear_on_submit=True):
            # Required fields
            st.markdown("##### Required Information")
            name = st.text_input("Full Name*", key='name')
            plate_number = st.text_input("Vehicle Plate Number*", key='plate_number')
            id_number = st.text_input("ID Number*", key='id_number')

            # Optional fields
            st.markdown("##### Contact Information")
            phone_number = st.text_input("Phone Number", key='phone_number')
            email = st.text_input("Email Address", key='email')
            address = st.text_input("Address", key='address')

            # Visit details
            st.markdown("##### Visit Details")
            visit_purpose = st.text_input("Purpose of Visit*", key='visit_purpose')

            # Date selection
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                check_in_date = st.date_input(
                    "Check-in Date*",
                    min_value=datetime.now().date(),
                    value=datetime.now().date(),
                    key='check_in_date'
                )
            with date_col2:
                check_out_date = st.date_input(
                    "Check-out Date*",
                    min_value=check_in_date,
                    value=check_in_date + timedelta(days=1),
                    key='check_out_date'
                )

            submitted = st.form_submit_button("Submit Registration")

            if submitted:
                validation_failed = False

                # Validation checks
                if not all([name, plate_number, id_number, visit_purpose]):
                    st.error("Please fill in all required fields marked with *")
                    validation_failed = True

                if plate_number and not validate_plate_number(plate_number):
                    st.error("Invalid plate number format")
                    validation_failed = True

                if email and not validate_email(email):
                    st.error("Invalid email format")
                    validation_failed = True

                if not validation_failed:
                    guest_data = {
                        "name": name,
                        "plate_number": plate_number.upper(),
                        "id_number": id_number,
                        "phone_number": phone_number,
                        "email": email,
                        "address": address,
                        "visit_purpose": visit_purpose,
                        "check_in_date": check_in_date,
                        "check_out_date": check_out_date
                    }

                    if insert_guest(guest_data):
                        # Set success message and timestamp
                        st.session_state.show_success = True
                        st.session_state.success_time = time.time()
                        st.rerun()

    # Right column - Recent Registrations
    with col2:

        st.subheader("Recent Guest Registrations")

        # Fetch and display recent registrations
        df = fetch_recent_registrations()

        if not df.empty:
            df['Check-in Date'] = pd.to_datetime(df['Check-in Date']).dt.strftime('%d-%m-%Y')
            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No recent registrations found")

        # Auto refresh for both the table and success message state
        st_autorefresh(interval=2000, key="page_refresh")
