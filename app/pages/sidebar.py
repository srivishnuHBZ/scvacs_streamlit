import streamlit as st
import time
from streamlit_option_menu import option_menu
from app.utils.session import is_logged_in
from app.database import approve_guest, reject_guest, fetch_pending_guests
from streamlit_autorefresh import st_autorefresh

# Navigation options for logged-in users
LOGGED_IN_MENU = {
    "View Vehicle Details": "view_vehicle_page",
    "Guest Pass Registration": "guest_pass_registration",
    "Vehicle History": "history_page",
    "Logout": None,
}

def handle_guest_approval(guest, index):
    """Handle the approval/rejection of a guest."""
    guest_key = guest['Plate Number']
    col1, col2 = st.columns(2, gap="small")

    # Variable to store the message
    message_placeholder = st.empty()

    def process_action(action, function, success_message, message_type="success"):
        try:
            function(guest['Plate Number'])
            st.session_state.guest_actions[guest_key] = action
            
            # Display message once, spanning both columns
            with message_placeholder:
                if message_type == "success":
                    st.success(success_message)
                elif message_type == "warning":
                    st.warning(success_message)
            
            time.sleep(5)
            st.session_state.pending_guests = fetch_pending_guests()
            st.rerun()
        except Exception as e:
            message_placeholder.error(f"Error {action} guest: {e}")

    # Custom button styling for full width
    button_style = """
    <style>
    div.stButton > button {
        width: 100%;
        font-size: 16px;
    }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    
    # Buttons in their respective columns
    with col1:
        if st.button("✓ Approve", key=f"approve_{index}", type="primary"):
            process_action(
                'approved', 
                approve_guest, 
                f"Guest {guest['Name']} ({guest['Plate Number']}) Approved.", 
                message_type="success"
            )

    with col2:
        if st.button("✗ Reject", key=f"reject_{index}", type="secondary"):
            process_action(
                'rejected', 
                reject_guest, 
                f"Guest {guest['Name']} ({guest['Plate Number']}) Rejected.", 
                message_type="warning"
            )

def render_pending_guests_section(latest_pending_guests=None):
    """Render the pending guest approvals section."""
    st.markdown("### Pending Guest Approvals")

    # Fetch latest pending guests if not provided
    if latest_pending_guests is None:
        try:
            latest_pending_guests = fetch_pending_guests()
        except Exception as e:
            st.error(f"Error fetching pending guests: {e}")
            return

    # Initialize guest actions if not exists
    st.session_state.setdefault('guest_actions', {})

    if latest_pending_guests is not None and not latest_pending_guests.empty:
        # Filter pending guests who haven't been acted upon
        pending_guests = latest_pending_guests[
            ~latest_pending_guests['Plate Number'].isin(st.session_state.guest_actions.keys())
        ]

        if not pending_guests.empty:
            st.write(f"Total pending guests: {len(pending_guests)}")
            for index, guest in pending_guests.iterrows():
                with st.expander(f"📋 {guest['Name']} ({guest['Plate Number']})"):
                    st.markdown(f"""
                        **Vehicle Type:** {guest['Vehicle Type']}  
                        **Phone:** {guest['Phone Number']}  
                        **Purpose:** {guest['Visit Purpose']}  
                        **Check-in:** {guest['Check-in Date']}  
                        **Check-out:** {guest['Check-out Date']}
                    """)
                    handle_guest_approval(guest, index)
        else:
            st.info("👍 No pending approvals")
    else:
        st.info("👍 No pending approvals")

    st_autorefresh(interval=2000, key="pending_refresh")
    
def render_sidebar(latest_pending_guests=None):
    """Render the main sidebar with navigation and pending approvals."""
    with st.sidebar:
        if not is_logged_in():
            selected = option_menu(
                "Main Menu",
                ["Login"],
                icons=["box-arrow-in-right"],
                menu_icon="list",
                default_index=0,
            )
            return selected

        # Main navigation menu
        selected = option_menu(
            "Main Menu",
            list(LOGGED_IN_MENU.keys()),
            icons=["eye", "person-plus", "clock-history", "box-arrow-right"],
            menu_icon="list",
            default_index=0,
        )
        
        # Add separator between menu and pending approvals
        st.markdown("---")
        
        # Render pending guests section
        render_pending_guests_section(latest_pending_guests)
        
        return selected