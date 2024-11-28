import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from app.database import fetch_vehicle_history
from streamlit_autorefresh import st_autorefresh

def render_page():
    st.title("Vehicle History")

    # Preserve login state while clearing other session state variables
    login_state = st.session_state.get("logged_in", False)
    session_vars_to_keep = ["logged_in"]
    
    # Clear all stored values in session state except login state
    for key in list(st.session_state.keys()):
        if key not in session_vars_to_keep:
            del st.session_state[key]
    
    # Restore login state
    st.session_state["logged_in"] = login_state
    
    # Auto refresh every 1 second (1000 milliseconds)
    st_autorefresh(interval=1000, key="vehicle_history_refresh")

    # Create three columns for filtering options
    col1, col2, col3 = st.columns(3)
    with col1:
        plate_number_filter = st.text_input("Search by Plate Number:", placeholder="Enter plate number...")
    with col2:
        start_date = st.date_input(
            "Start Date (Optional):",
            value=None,
            help="Show results from this date onwards. Leave empty to show all historical data.",
        )
    with col3:
        end_date = st.date_input(
            "End Date (Optional):",
            value=None,
            help="Show results until this date. Leave empty to show up to latest data.",
        )

    # Fetch the data from the database
    data = fetch_vehicle_history()

    # Check if data is a DataFrame before checking if it's empty
    if isinstance(data, pd.DataFrame):
        if not data.empty:
            # Ensure the 'Timestamp' column exists
            if 'Timestamp' in data.columns:
                # Apply filtering based on the plate number
                if plate_number_filter:
                    data = data[data['Plate Number'].str.contains(plate_number_filter, case=False, na=False)]
                
                # Convert 'Timestamp' to datetime and handle invalid entries
                data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')
                
                # Drop rows with invalid dates
                data = data.dropna(subset=['Timestamp'])
                
                # Apply start date filter if provided
                if start_date:
                    data = data[data['Timestamp'] >= pd.to_datetime(start_date)]
                
                # Apply end date filter if provided
                if end_date:
                    # Adjust end_date to include the entire day
                    adjusted_end_date = end_date + timedelta(days=1)
                    data = data[data['Timestamp'] < pd.to_datetime(adjusted_end_date)]
                
                # Display the filtered data
                st.dataframe(data, use_container_width=True)
            else:
                st.error("'Timestamp' column is missing from the data.")
        else:
            st.warning("No data available.")
    else:
        st.error(data)  # Handle the case where data is not a DataFrame