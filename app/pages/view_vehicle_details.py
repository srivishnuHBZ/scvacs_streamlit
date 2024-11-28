import streamlit as st
from app.database import SessionLocal, engine
from sqlalchemy import text
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from app.database import check_for_updates

def display_vehicle_details(vehicle_df, status):
    if status == 1:  # Registered vehicle
        st.markdown(
            "<div style='background-color: green; padding: 5px; border-radius: 5px;'>"
            "<h2 style='color: white; text-align: center;'>Registered Vehicle Detected</h2></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Number Plate", vehicle_df['plate_number'].values[0])
            st.metric("Owner's Name", vehicle_df['owner_name'].values[0])
            st.metric("Address", vehicle_df['address'].values[0])
            st.metric("Phone Number", vehicle_df['phone_number'].values[0])
            st.metric("Pass Expiry Date", vehicle_df['pass_expiry_date'].values[0])
        with col2:
            st.metric("Make", vehicle_df['make'].values[0])
            st.metric("Model", vehicle_df['model'].values[0])
            st.metric("Color", vehicle_df['color'].values[0])
            st.metric("Vehicle Type", vehicle_df['vehicle_type'].values[0])
            st.metric("Detection Time", vehicle_df['detection_time'].values[0])
    else:
        st.markdown(
            "<div style='background-color: red; padding: 5px; border-radius: 5px;'>"
            "<h2 style='color: white; text-align: center;'>Unregistered Vehicle Detected</h2></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Number Plate", vehicle_df['plate_number'].values[0])
            st.metric("Confidence Score", vehicle_df['confidence'].values[0])
        with col2:
            st.metric("Registration Status", vehicle_df['registration_status'].values[0])
            st.metric("Detection Time", vehicle_df['detection_time'].values[0])

def render_page():
    st.markdown("<h1 style='text-align: center;'>Smart Campus Vehicle Access Control System</h1>", unsafe_allow_html=True)
    # Initialize state
    if "vehicle_details" not in st.session_state:
        st.session_state.vehicle_details = pd.DataFrame()
    if "status" not in st.session_state:
        st.session_state.status = None

    st_autorefresh(interval=3000, key="vehicle_history_refresh")

    try:
        status, vehicle_df = check_for_updates()

        if vehicle_df is not None and not vehicle_df.empty:
            st.session_state.vehicle_details = vehicle_df
            st.session_state.status = status

        if not st.session_state.vehicle_details.empty:
            display_vehicle_details(st.session_state.vehicle_details, st.session_state.status)
        else:
            st.markdown(
            "<div style='background-color: #89CFF0; padding: 5px; border-radius: 5px;'>"
            "<h2 style='color: white; text-align: center;'>Vehicle Detection In Progress...</h2></div>",
            unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    render_page()
