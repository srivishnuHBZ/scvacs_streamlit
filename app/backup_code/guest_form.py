import streamlit as st
import time
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base, SessionLocal

# Define the SQLAlchemy model
class GuestTemp(Base):
    __tablename__ = "guest_temp"
    
    guest_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text('NEWID()'))
    name = Column(String(255), nullable=False)
    plate_number = Column(String(50), nullable=False)
    vehicle_type = Column(String(30))
    id_number = Column(String(50), nullable=False)
    phone_number = Column(String(15))
    email = Column(String(100))
    address = Column(String(100))
    visit_purpose = Column(String(255))
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)

def calculate_checkout_date(check_in_date, duration):
    if duration == "1 Hour":
        return check_in_date + timedelta(hours=1)
    elif duration == "Half Day":
        return check_in_date + timedelta(hours=12)
    elif duration == "1 Day":
        return check_in_date + timedelta(days=1)
    elif duration == "2 Days":
        return check_in_date + timedelta(days=2)
    return check_in_date

def show_pending_verification():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #1E88E5;'>Pending Verification from Guards</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 2rem;'>Please wait while our security personnel verify your registration.</p>", unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.5)

def render_guest_page():
    # Initialize the state
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

    if st.session_state.form_submitted:
        # Show loading screen
        show_pending_verification()
        return

    # Add this line to create a container for the form
    form_container = st.container()

    with form_container:
        st.markdown("<img src='https://seeklogo.com/images/U/Universiti_Malaysia_Sabah-logo-590ACB05AA-seeklogo.com.png' width='250' style='display: block; margin: 0 auto;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Guest Vehicle Registration Form</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("guest_registration"):
            # Personal Information
            st.subheader("Personal Information")
            name = st.text_input("Full Name *")
            id_number = st.text_input("IC Number/Passport *")
            phone_number = st.text_input("Phone Number *")
            email = st.text_input("Email Address")
            address = st.text_input("Address")
            
            # Vehicle Information
            st.subheader("Vehicle Information")
            plate_number = st.text_input("Vehicle Plate Number *")
            vehicle_type = st.selectbox("Vehicle Type", ["Car", "Motorcycle", "Van", "Others"])
            
            # Visit Details
            st.subheader("Visit Details")
            visit_purpose = st.text_area("Purpose of Visit *")
            check_in_date = st.date_input("Visit Date")
            duration = st.selectbox("Duration of Visit", ["1 Hour", "Half Day", "1 Day", "2 Days"])
            
            submitted = st.form_submit_button("Submit Registration")
            
            if submitted:
                if not all([name, id_number, plate_number, phone_number, visit_purpose]):
                    st.error("Please fill in all required fields")
                    return

                try:
                    check_in_datetime = datetime.now()
                    check_out_datetime = calculate_checkout_date(check_in_datetime, duration)

                    new_guest = GuestTemp(
                        name=name,
                        plate_number=plate_number,
                        vehicle_type=vehicle_type,
                        id_number=id_number,
                        phone_number=phone_number,
                        email=email,
                        address=address,
                        visit_purpose=visit_purpose,
                        check_in_date=check_in_datetime,
                        check_out_date=check_out_datetime
                    )

                    db = SessionLocal()
                    try:
                        db.add(new_guest)
                        db.commit()
                        st.session_state.form_submitted = True
                        
                        # Clear the form container after submission
                        form_container.empty()
                        
                        st.rerun()  # Replace this in real implementation
                        
                    except Exception as e:
                        db.rollback()
                        st.error(f"An error occurred while saving the registration: {str(e)}")
                    finally:
                        db.close()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")