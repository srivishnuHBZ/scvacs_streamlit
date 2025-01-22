from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse
import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

server = "34.60.160.28"  
database = "scvacs"       
username = "sqlserver"    
password = urllib.parse.quote_plus("scvacs@1234")  # Escape special characters in password
port = "1433"  # Default MS SQL Server port

# SQLAlchemy connection string using pytds
DATABASE_URL = (
    f"mssql+pytds://{username}:{password}@{server}:{port}/{database}"
)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True)  # Echo=True for detailed logs
# engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Queries from vehicle_history.py

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

# Queries from guess_pass_registration.py

def insert_guest(guest_data):
    try:
        query = """
        INSERT INTO guest (
            name, plate_number, id_number, phone_number, email,
            address, visit_purpose, check_in_date, check_out_date, is_approved
        ) VALUES (
            :name, :plate_number, :id_number, :phone_number, :email, 
            :address, :visit_purpose, :check_in_date, :check_out_date, :is_approved
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
            WHERE is_approved = 1
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

def get_latest_vehicle_detail():
    """
    Query and return the most recent vehicle detail from vehicle_history.
    Handles three cases:
    1. Registered vehicles (join with registered_vehicle and users tables)
    2. Approved guests (join with guest table)
    3. Unregistered vehicles
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

        # First check if it's a guest vehicle
        guest_query = text("""
            SELECT 
                vh.plate_number,
                g.name as guest_name,
                g.phone_number,
                g.email,
                g.visit_purpose,
                g.check_in_date,
                g.check_out_date,
                g.is_approved,
                vh.timestamp as detection_time
            FROM vehicle_history vh
            INNER JOIN guest g ON vh.plate_number = g.plate_number
            WHERE vh.plate_number = :plate_number
        """)
        guest_result = session.execute(guest_query, {'plate_number': latest_vehicle.plate_number})
        guest_data = guest_result.fetchone()

        if guest_data:
            # It's a guest vehicle
            return 2, pd.DataFrame([{
                'guest_name' : guest_data.guest_name,
                'plate_number': guest_data.plate_number,
                'phone_number': guest_data.phone_number,
                'visit_purpose': guest_data.visit_purpose,
                'check_in_date': guest_data.check_in_date.strftime('%d-%m-%Y %H:%M:%S'),
                'check_out_date': guest_data.check_out_date.strftime('%d-%m-%Y %H:%M:%S'),
                'is_approved': guest_data.is_approved
            }])
        
        # If not a guest, check if it's a registered vehicle
        elif latest_vehicle.registration_status:
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
            # Unregistered vehicle
            return 0, pd.DataFrame([{
                'plate_number': latest_vehicle.plate_number,
                'confidence': latest_vehicle.confidence,
                'registration_status': latest_vehicle.registration_status,
                'detection_time': latest_vehicle.timestamp.strftime('%d-%m-%Y %H:%M:%S')
            }])

# Queries from sidebar.py

def fetch_pending_guests():
    """Fetch all pending guests from guest_temp table."""
    query = """
    SELECT name, plate_number, vehicle_type, phone_number, visit_purpose, check_in_date, check_out_date 
    FROM guest_temp
    """
    with engine.connect() as conn:
        try:
            result = conn.execute(text(query)).fetchall()
            return pd.DataFrame(result, columns=["Name", "Plate Number", "Vehicle Type", "Phone Number", "Visit Purpose", "Check-in Date", "Check-out Date"])
        except SQLAlchemyError as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()

def approve_guest(plate_number):
    try:
        with SessionLocal() as session:
            insert_query = """
            INSERT INTO guest (name, plate_number, id_number, phone_number, email, address, visit_purpose, check_in_date, check_out_date, is_approved)
            SELECT name, plate_number, id_number, phone_number, email, address, visit_purpose, check_in_date, check_out_date, :is_approved
            FROM guest_temp WHERE plate_number = :plate_number
            """
            delete_query = "DELETE FROM guest_temp WHERE plate_number = :plate_number"
            session.execute(text(insert_query), {"plate_number": plate_number, "is_approved": "1"})
            session.execute(text(delete_query), {"plate_number": plate_number})
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Error approving guest: {e}")

def reject_guest(plate_number):
    try:
        with SessionLocal() as session:
            insert_query = """
            INSERT INTO guest (name, plate_number, id_number, phone_number, email, address, visit_purpose, check_in_date, check_out_date, is_approved)
            SELECT name, plate_number, id_number, phone_number, email, address, visit_purpose, check_in_date, check_out_date, :is_approved
            FROM guest_temp WHERE plate_number = :plate_number
            """
            delete_query = "DELETE FROM guest_temp WHERE plate_number = :plate_number"
            session.execute(text(insert_query), {"plate_number": plate_number, "is_approved": "0"})
            session.execute(text(delete_query), {"plate_number": plate_number})
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Error rejecting guest: {e}")
        
        
# Queries from analytics.py

def get_total_vehicles_today(conn):
    query = """
    SELECT COUNT(DISTINCT plate_number) as total
    FROM vehicle_history
    WHERE CAST(timestamp AS DATE) = CAST(GETDATE() AS DATE)
    """
    result = conn.execute(text(query)).fetchone()
    return result.total

def get_unauthorized_attempts(conn):
    query = """
    SELECT COUNT(DISTINCT plate_number) as total
    FROM vehicle_history
    WHERE registration_status = 0
    AND CAST(timestamp AS DATE) = CAST(GETDATE() AS DATE)
    """
    result = conn.execute(text(query)).fetchone()
    return result.total

def get_guest_passes_issued(conn):
    query = """
    SELECT COUNT(*) as total
    FROM guest
    WHERE is_approved = 1
    AND CAST(created_at AS DATE) = CAST(GETDATE() AS DATE)
    """
    result = conn.execute(text(query)).fetchone()
    return result.total

def get_peak_hour_traffic(conn):
    query = """
    SELECT 
        DATEPART(HOUR, timestamp) as hour,
        COUNT(*) as traffic_count
    FROM vehicle_history
    WHERE CAST(timestamp AS DATE) = CAST(GETDATE() AS DATE)
    GROUP BY DATEPART(HOUR, timestamp)
    ORDER BY traffic_count DESC
    """
    result = conn.execute(text(query)).fetchone()
    return f"{result.hour:02d}:00" if result else "N/A"

def get_vehicle_trends(conn):
    query = """
    SELECT 
        CAST(timestamp AS DATE) as date,
        COUNT(plate_number) as total_vehicles,
        SUM(CASE WHEN registration_status = 0 THEN 1 ELSE 0 END) as unauthorized,
        SUM(CASE WHEN registration_status = 1 THEN 1 ELSE 0 END) as authorized
    FROM vehicle_history
    WHERE timestamp >= DATEADD(day, -7, GETDATE())
    GROUP BY CAST(timestamp AS DATE)
    ORDER BY date
    """
    return pd.read_sql(query, conn)

def get_hourly_distribution(conn):
    query = """
    SELECT 
        DATEPART(HOUR, timestamp) as hour,
        COUNT(*) as count
    FROM vehicle_history
    WHERE CAST(timestamp AS DATE) = CAST(GETDATE() AS DATE)
    GROUP BY DATEPART(HOUR, timestamp)
    ORDER BY hour
    """
    return pd.read_sql(query, conn)

def get_todays_vehicle_history(conn):
    query = """
    SELECT 
        plate_number,
        confidence,
        timestamp,
        CASE WHEN registration_status = 1 THEN 'Registered' ELSE 'Unregistered' END as status
    FROM vehicle_history
    WHERE CAST(timestamp AS DATE) = CAST(GETDATE() AS DATE)
    ORDER BY timestamp DESC
    """
    return pd.read_sql(query, conn)

def get_todays_guests(conn):
    query = """
    SELECT 
        name,
        plate_number,
        phone_number,
        visit_purpose,
        check_in_date,
        check_out_date,
        CASE WHEN is_approved = 1 THEN 'Approved' ELSE 'Rejected' END as status
    FROM guest
    WHERE CAST(created_at AS DATE) = CAST(GETDATE() AS DATE)
    ORDER BY created_at DESC
    """
    return pd.read_sql(query, conn)

