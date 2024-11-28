import streamlit as st
from app.database import SessionLocal, engine
from sqlalchemy import text
import pandas as pd
from streamlit_autorefresh import st_autorefresh

def get_latest_vehicle_detail():
    """
    Query and return the most recent vehicle detail from vehicle_history.
    If registered (status=1), join with registered_vehicle and users tables.
    """
    with SessionLocal() as session:
        # Get the latest vehicle_history entry
        latest_vehicle_query = text("""
            SELECT TOP 1
                vh.vehicle_history_id,
                vh.plate_number,
                vh.confidence,
                vh.registration_status,
                vh.timestamp
            FROM vehicle_history vh
            ORDER BY vh.timestamp DESC
        """)
        latest_vehicle = session.execute(latest_vehicle_query).fetchone()

        if not latest_vehicle:
            return None, None

        # If vehicle is registered, get additional details
        if latest_vehicle.registration_status:
            registered_query = text("""
                SELECT 
                    vh.plate_number,
                    u.fullname as owner_name,
                    u.address,
                    u.phone_number,
                    rv.pass_expiry_date,
                    vh.registration_status,
                    rv.make,
                    rv.model,
                    rv.color,
                    rv.vehicle_type,
                    vh.timestamp as detection_time
                FROM vehicle_history vh
                INNER JOIN registered_vehicle rv ON vh.plate_number = rv.number_plate
                INNER JOIN users u ON rv.username = u.username
                WHERE vh.plate_number = :plate_number
            """)
            result = session.execute(registered_query, {'plate_number': latest_vehicle.plate_number})
            fetched_data = result.fetchall()
            registered_vehicle_details = [
                {
                    **dict(row._mapping),
                    'pass_expiry_date': row.pass_expiry_date.strftime('%d-%m-%Y'),
                    'detection_time': row.detection_time.strftime('%d-%m-%Y %H:%M:%S')
                }
                for row in fetched_data
            ]
            return 1, pd.DataFrame(registered_vehicle_details)
        else:
            return 0, pd.DataFrame([{
                'plate_number': latest_vehicle.plate_number,
                'confidence': latest_vehicle.confidence,
                'registration_status': latest_vehicle.registration_status,
                'detection_time': latest_vehicle.timestamp.strftime('%d-%m-%Y %H:%M:%S')
            }])

def check_for_updates():
    """
    Check for updates in the vehicle_history table by querying the latest timestamp.
    Only fetch new data if the latest timestamp has changed.
    """
    with SessionLocal() as session:
        latest_timestamp_query = text("SELECT MAX(timestamp) AS latest_timestamp FROM vehicle_history")
        result = session.execute(latest_timestamp_query).fetchone()
        latest_timestamp = result.latest_timestamp

        if (
            'latest_timestamp' in st.session_state 
            and st.session_state.latest_timestamp == latest_timestamp
        ):
            return None, None

        st.session_state.latest_timestamp = latest_timestamp
        return get_latest_vehicle_detail()

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
