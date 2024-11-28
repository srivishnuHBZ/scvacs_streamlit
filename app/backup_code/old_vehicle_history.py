import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from app.database import fetch_vehicle_history

def render_page():
    st.title("Vehicle History")

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

    # Create a placeholder for the table
    table_placeholder = st.empty()

    # Infinite loop to refresh data
    while True:
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
                    # Drop rows with invalid dates (optional)
                    data = data.dropna(subset=['Timestamp'])

                    # Apply start date filter if provided
                    if start_date:
                        data = data[data['Timestamp'] >= pd.to_datetime(start_date)]

                    # Apply end date filter if provided
                    if end_date:
                        # Adjust end_date to include the entire day
                        adjusted_end_date = end_date + timedelta(days=1)
                        data = data[data['Timestamp'] < pd.to_datetime(adjusted_end_date)]

                    # Display the filtered data in the placeholder
                    table_placeholder.dataframe(data, use_container_width=True)
                else:
                    st.error("'Timestamp' column is missing from the data.")
            else:
                st.warning("No data available.")
        else:
            st.error(data)  # Handle the case where data is not a DataFrame

        # Refresh interval
        time.sleep(0.5)
        
