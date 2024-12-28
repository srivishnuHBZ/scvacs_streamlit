import streamlit as st
import time
import os
import base64
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base, SessionLocal
from sqlalchemy.exc import SQLAlchemyError

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
    
    # Initialize session state for tracking verification status
    if 'verification_complete' not in st.session_state:
        st.session_state.verification_complete = False
        st.session_state.approval_status = None
        st.session_state.verification_start_time = datetime.now()
    
    with col2:
        if not st.session_state.verification_complete:
            verification_header = st.empty()
            verification_message = st.empty()
            
            verification_header.markdown("<h2 style='text-align: center; color: #1E88E5;'>Pending Verification from Guards</h2>", 
                                    unsafe_allow_html=True)
            verification_message.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 2rem;'>"
                                    "Please wait while our security personnel verify your registration.</p>", 
                                    unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            # Calculate timeout (5 minutes)
            timeout_duration = timedelta(minutes=5)
            
            try:
                with SessionLocal() as session:
                    progress = 0  # Initial progress value
                    while not st.session_state.verification_complete:
                        # Check if timeout has been reached
                        if datetime.now() - st.session_state.verification_start_time > timeout_duration:
                            st.error("Verification timeout reached. Please try again or contact security.")
                            break
                        
                        # Query the guest table using plate number
                        result = session.execute(
                            text("""
                                SELECT TOP 1 is_approved
                                FROM guest
                                WHERE plate_number = :plate_number
                                ORDER BY created_at DESC
                            """),
                            {"plate_number": st.session_state.get('plate_number', '')}
                        ).fetchone()
                        
                        if result:
                            is_approved = result[0]
                            
                            if is_approved is not None:  # Status has been updated
                                st.session_state.verification_complete = True
                                st.session_state.approval_status = is_approved
                                
                                # Clear the verification UI
                                verification_header.empty()
                                verification_message.empty()
                                progress_bar.empty()
                                status_placeholder.empty()
                                
                                # Display the final status
                                if is_approved:
                                    st.markdown(""" 
                                        <div style='display: flex; justify-content: center;'>
                                            <div style='background-color: #e7f3eb; padding: 20px; border-radius: 10px; 
                                                    border-left: 5px solid #28a745; margin: 20px 0; text-align: center;'>
                                                <h3 style='color: #28a745; margin: 0 0 10px 0;'>
                                                    ✅ Registration Approved
                                                </h3>
                                                <p style='margin: 0; color: #2c3e50;'>
                                                    Your vehicle registration has been approved. You may proceed to the entrance.
                                                </p>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Add instructions  
                                    st.markdown("<p style='text-align: center; margin-top: 20px;'>"
                                              "Please show this screen to the security guard at the entrance.</p>", 
                                              unsafe_allow_html=True)
                                else:
                                    st.markdown(""" 
                                        <div style='display: flex; justify-content: center;'>
                                            <div style='background-color: #fbebed; padding: 20px; border-radius: 10px; 
                                                    border-left: 5px solid #dc3545; margin: 20px 0; text-align: center;'>
                                                <h3 style='color: #dc3545; margin: 0 0 10px 0;'>
                                                    ❌ Registration Rejected  
                                                </h3>
                                                <p style='margin: 0; color: #2c3e50;'>
                                                    We're sorry, but your registration has been rejected.
                                                    <br><br>
                                                    Please contact the security officer for more information.  
                                                </p>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)

                                break
                        
                        # Update progress bar incrementally
                        progress += 3  # Adjust the increment value (e.g., 5%) per loop
                        if progress > 100:
                            progress = 100
                        progress_bar.progress(progress)
                        
                        # Update the status message to keep the user informed
                        status_placeholder.markdown("<p style='text-align: center; color: #666;'>""Checking verification status...</p>", unsafe_allow_html=True)
                        time.sleep(2)  # Delay to simulate processing time
                    
            except SQLAlchemyError as e:
                st.error(f"Database error occurred: {str(e)}")
                st.session_state.verification_complete = True
            except Exception as e:  
                st.error(f"An unexpected error occurred: {str(e)}")
                st.session_state.verification_complete = True

def show_registration_form(form_container):
    with form_container:
        #st.markdown("<img src='https://seeklogo.com/images/U/Universiti_Malaysia_Sabah-logo-590ACB05AA-seeklogo.com.png' width='250' style='display: block; margin: 0 auto;'>", unsafe_allow_html=True)
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
            plate_number = st.text_input("Vehicle Plate Number *").upper()
            vehicle_type = st.selectbox("Vehicle Type", ["Car", "Motorcycle", "Van", "Others"])
            
            # Visit Details  
            st.subheader("Visit Details")
            visit_purpose = st.text_area("Purpose of Visit *")
            check_in_date = st.date_input("Visit Date")
            duration = st.selectbox("Duration of Visit", ["1 Hour", "Half Day", "1 Day", "2 Days"], index=0)
            
            submitted = st.form_submit_button("Submit Registration")
            
            if submitted:
                if not all([name, id_number, plate_number, phone_number, visit_purpose]):
                    st.error("Please fill in all required fields")
                else:
                    return True, name, id_number, phone_number, email, address, plate_number, vehicle_type, visit_purpose, check_in_date, duration
    
    return False, None, None, None, None, None, None, None, None, None, None

def save_guest_registration(name, id_number, phone_number, email, address, plate_number, vehicle_type, visit_purpose, check_in_date, duration):
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
            return True
        except Exception as e:
            db.rollback()
            st.error(f"An error occurred while saving the registration: {str(e)}")
            return False
        finally:
            db.close()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return False

def render_guest_page():
    # Wake up the DB with a simple query, only if not done already
    if "db_woken_up" not in st.session_state:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))  # Simple query to wake up the DB
            db.commit()
            st.session_state.db_woken_up = True  # Mark the DB as awake
        except Exception as e:
            st.error(f"An error occurred while connecting to the database: {str(e)}")
        finally:
            db.close()

    # Initialize the state
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

    if st.session_state.form_submitted:
        show_pending_verification()
        return

    form_container = st.container()
    submitted, name, id_number, phone_number, email, address, plate_number, vehicle_type, visit_purpose, check_in_date, duration = show_registration_form(form_container)
    
    if submitted:
        if save_guest_registration(name, id_number, phone_number, email, address, plate_number, vehicle_type, visit_purpose, check_in_date, duration):
            st.session_state.form_submitted = True
            st.session_state.plate_number = plate_number
            st.rerun()