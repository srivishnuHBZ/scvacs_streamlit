import streamlit as st
from streamlit_option_menu import option_menu
from app.utils.session import set_logged_in, is_logged_in
from app.pages.login import render_page as login_page
from app.pages.view_vehicle_details import render_page as view_vehicle_page
from app.pages.guest_pass_registration import render_page as guest_pass_registration
from app.pages.vehicle_history import render_page as history_page
from app.pages.guest_form import render_guest_page
from app.database import fetch_pending_guests, approve_guest, reject_guest

# Set page configuration
st.set_page_config(
    page_title="Smart Campus Vehicle Access Control System",  
    page_icon="🚗", 
    layout="wide"
)

# Navigation options for logged-in users
LOGGED_IN_MENU = {
    "View Vehicle Details": view_vehicle_page,
    "Guest Pass Registration": guest_pass_registration,
    "Vehicle History": history_page,
    "Logout": None,  # Logout is handled separately
}

def render_pending_guests_section():
    st.subheader("Pending Guest Approvals")
    df = fetch_pending_guests()
    
    if not df.empty:
        for index, guest in df.iterrows():
            st.write(f"**{guest['Name']}**")
            st.write(f"Plate Number: {guest['Plate Number']}")
            st.write(f"Vehicle Type: {guest['Vehicle Type']}")
            st.write(f"Phone Number: {guest['Phone Number']}")
            st.write(f"Visit Purpose: {guest['Visit Purpose']}")
            st.write(f"Check-in Date: {guest['Check-in Date']}")
            st.write(f"Check-out Date: {guest['Check-out Date']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Approve {guest['Plate Number']}", key=f"approve_{index}"):
                    if 'action_done' not in st.session_state:
                        approve_guest(guest['Plate Number'])
                        st.session_state.action_done = True
                        st.rerun()
            with col2:
                if st.button(f"Reject {guest['Plate Number']}", key=f"reject_{index}"):
                    if 'action_done' not in st.session_state:
                        reject_guest(guest['Plate Number'])
                        st.session_state.action_done = True
                        st.rerun()
    else:
        st.info("No pending approvals.")
        
def render_sidebar():
    with st.sidebar:
        if not is_logged_in():
            return option_menu(
                "Main Menu",
                ["Login"],
                icons=["box-arrow-in-right"],
                menu_icon="list",
                default_index=0,
            )

        selected = option_menu(
            "Main Menu",
            list(LOGGED_IN_MENU.keys()),
            icons=["eye", "person-plus", "clock-history", "box-arrow-right"],
            menu_icon="list",
            default_index=0,
        )
        
        # Add Pending Approvals directly to the sidebar
        st.markdown("### Pending Guest Approvals")
        
        df = fetch_pending_guests()
        if not df.empty:
            for index, guest in df.iterrows():
                with st.expander(f"{guest['Name']} ({guest['Plate Number']})"):
                    st.write(f"**Phone Number:** {guest['Phone Number']}")
                    st.write(f"**Vehicle Type:** {guest['Vehicle Type']}")
                    st.write(f"**Visit Purpose:** {guest['Visit Purpose']}")
                    st.write(f"**Check-in Date:** {guest['Check-in Date']}")
                    st.write(f"**Check-out Date:** {guest['Check-out Date']}")

                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"Approve", key=f"approve_{index}"):
                            approve_guest(guest['Plate Number'])
                            st.success(f"Approved {guest['Name']}")
                            st.rerun()
                    with col2:
                        if st.button(f"Reject", key=f"reject_{index}"):
                            reject_guest(guest['Plate Number'])
                            st.warning(f"Rejected {guest['Name']}")
                            st.rerun()
        else:
            st.info("No pending approvals.")

        return selected
        

def get_page_route():
    # Get the query parameters using the new method
    return st.query_params.get("page", "main")

def main():
    # Check the route
    route = get_page_route()
    
    if route == "guest":
        # Render guest page without sidebar
        render_guest_page()
    else:
        # Regular admin portal with sidebar
        selected = render_sidebar()
        
        # Your existing routing logic
        if selected == "Login":
            if not is_logged_in():
                login_page()
            else:
                st.success("You are already logged in! Navigate using the menu.")
        elif is_logged_in():
            if selected in LOGGED_IN_MENU and LOGGED_IN_MENU[selected]:
                LOGGED_IN_MENU[selected]()
            elif selected == "Logout":
                st.session_state["logged_in"] = False
                st.success("Logged out successfully!")
                st.rerun()
        else:
            st.warning("You must log in to access this page.")
            login_page()

if __name__ == "__main__":
    main()