import streamlit as st
import streamlit_autorefresh
from app.pages.sidebar import render_sidebar
from app.utils.session import set_logged_in, is_logged_in
from app.pages.login import render_page as login_page
from app.pages.view_vehicle_details import render_page as view_vehicle_page
from app.pages.guest_pass_registration import render_page as guest_pass_registration
from app.pages.vehicle_history import render_page as history_page
from app.pages.guest_form import render_guest_page
from app.pages.sidebar import LOGGED_IN_MENU
from app.database import fetch_pending_guests
from app.pages.analytics import render_page as analytics_page

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "action_done" not in st.session_state:
        st.session_state.action_done = False
    if "guest_actions" not in st.session_state:
        st.session_state.guest_actions = {}

def get_page_route():
    """Get the current page route from query parameters."""
    return st.query_params.get("page", "main")

def handle_logout():
    """Handle user logout."""
    st.session_state.logged_in = False
    st.session_state.action_done = False
    st.success("👋 Logged out successfully!")
    st.rerun()

def main():
    # Initialize session state
    initialize_session_state()
    
    # Get route and check if it's guest page
    route = get_page_route()
    
    if route == "guest":
        # For guest page, set minimal page config without sidebar
        st.set_page_config(
            page_title="Guest Registration",
            page_icon="🚗",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        render_guest_page()
        return
    else:
        # For all other pages, use the default wide layout with sidebar
        st.set_page_config(
            page_title="Smart Campus Vehicle Access Control System",
            page_icon="🚗",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    # Fetch pending guests
    try:
        latest_pending_guests = fetch_pending_guests()
    except Exception as e:
        st.error(f"Error fetching pending guests: {e}")
        latest_pending_guests = None
    
    # Render sidebar with latest pending guests
    selected = render_sidebar()
    
    # Handle page routing
    if selected == "Login":
        if not is_logged_in():
            login_page()
        else:
            st.success("✅ You are already logged in! Use the menu to navigate.")
            
    elif is_logged_in():
        if selected == "Logout":
            handle_logout()
        elif selected in LOGGED_IN_MENU and LOGGED_IN_MENU[selected]:
            # Render the selected page
            page_function = globals()[LOGGED_IN_MENU[selected]]
            page_function()
    else:
        st.warning("🔒 You must log in to access this page.")
        login_page()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)  # This will show the full traceback in development