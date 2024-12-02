import streamlit as st
from streamlit_option_menu import option_menu
from app.utils.session import is_logged_in
from app.database import approve_guest, reject_guest, fetch_pending_guests

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
    col1, col2 = st.columns([1, 1])

    # Check if this guest has already been acted upon
    if guest_key in st.session_state.guest_actions:
        action = st.session_state.guest_actions[guest_key]
        st.info(f"Guest {guest['Name']} was {action}")
        return True

    with col1:
        if st.button("✓ Approve", key=f"approve_{index}", type="primary"):
            try:
                approve_guest(guest['Plate Number'])
                st.session_state.guest_actions[guest_key] = 'approved'
                # Force a refresh of pending guests
                st.session_state.pending_guests = fetch_pending_guests()
                st.rerun()
            except Exception as e:
                st.error(f"Error approving guest: {e}")

    with col2:
        if st.button("✗ Reject", key=f"reject_{index}", type="secondary"):
            try:
                reject_guest(guest['Plate Number'])
                st.session_state.guest_actions[guest_key] = 'rejected'
                # Force a refresh of pending guests
                st.session_state.pending_guests = fetch_pending_guests()
                st.rerun()
            except Exception as e:
                st.error(f"Error rejecting guest: {e}")

    return False

def render_pending_guests_section(latest_pending_guests=None):
    """Render the pending guests section in the sidebar."""
    st.markdown("### Pending Guest Approvals")

    # Ensure we have the latest pending guests
    if latest_pending_guests is None:
        try:
            latest_pending_guests = fetch_pending_guests()
        except Exception as e:
            st.error(f"Error fetching pending guests: {e}")
            return

    # Initialize guest actions if not exists
    if 'guest_actions' not in st.session_state:
        st.session_state.guest_actions = {}

    # Check if data exists and is not empty
    if latest_pending_guests is not None and not latest_pending_guests.empty:
        # Filter out guests that have already been acted upon
        pending_guests = latest_pending_guests[
            ~latest_pending_guests['Plate Number'].isin(st.session_state.guest_actions.keys())
        ]

        if not pending_guests.empty:
            # Debug print to verify all guests are being processed
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