from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse
import pandas as pd
import streamlit as st

server = "34.30.185.244"  
database = "scvacs"       
username = "sqlserver"    
password = urllib.parse.quote_plus("scvacs@1234")  # Escape special characters in password
port = "1433"  # Default SQL Server port

# SQLAlchemy connection string using pytds
DATABASE_URL = (
    f"mssql+pytds://{username}:{password}@{server}:{port}/{database}"
)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True)  # Echo=True for detailed logs
# engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def fetch_vehicle_history():
    try:
        with engine.connect() as conn:
            query = """
                SELECT plate_number, confidence, timestamp, registration_status
                FROM vehicle_history
                ORDER BY timestamp DESC
            """
            result = conn.execute(text(query))
            data = pd.DataFrame(result.fetchall(), columns=["Plate Number", "Confidence", "Timestamp", "Registration Status"])
            data['Registration Status'] = data['Registration Status'].astype(int).replace({1: 'Registered', 0: 'Unregistered'})
            return data
    except Exception as e:
        return f"Error fetching vehicle history: {e}"

def insert_guest(guest_data):
    try:
        query = """
        INSERT INTO guest (
            name, plate_number, id_number, phone_number,
            email, address, visit_purpose, check_in_date, check_out_date
        ) VALUES (
            :name, :plate_number, :id_number, :phone_number,
            :email, :address, :visit_purpose, :check_in_date, :check_out_date
        )
        """
        with engine.connect() as conn:
            conn.execute(text(query), guest_data)
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Error inserting guest data: {e}")
        return False
    
def fetch_recent_registrations():
    try:
        with engine.connect() as conn:
            query = """
            SELECT name, plate_number, phone_number, check_in_date
            FROM guest
            ORDER BY created_at DESC
            """
            result = conn.execute(text(query))
            df = pd.DataFrame(result.fetchall(), 
                            columns=['Name', 'Plate Number', 'Phone Number', 'Check-in Date'])
            return df
    except Exception as e:
        st.error(f"Error fetching recent registrations: {e}")
        return pd.DataFrame()
    
# Queries from view_vehicle_details.py
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

# Queries from view_vehicle_details.py
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
