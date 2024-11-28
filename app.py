import streamlit as st
from streamlit_option_menu import option_menu
from app.utils.session import set_logged_in, is_logged_in
from app.pages.login import render_page as login_page
from app.pages.view_vehicle_details import render_page as view_vehicle_page
from app.pages.guest_pass_registration import render_page as guest_pass_registration
from app.pages.vehicle_history import render_page as history_page
import time
# Set page configuration
st.set_page_config(
    page_title="Smart Campus Vehicle Access Control System",  
    page_icon="🚗", 
    layout="wide",
)

# Navigation options for logged-in users
LOGGED_IN_MENU = {
    "View Vehicle Details": view_vehicle_page,
    "Guest Pass Registration": guest_pass_registration,
    "Vehicle History": history_page,
    "Logout": None,  # Logout is handled separately
}

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
        return option_menu(
            "Main Menu",
            list(LOGGED_IN_MENU.keys()),
            icons=["eye", "person-plus", "clock-history", "box-arrow-right"],
            menu_icon="list",
            default_index=0,
        )

def main():
    selected = render_sidebar()

    # Route based on selected option
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
        # Fallback if unauthorized access is attempted
        st.warning("You must log in to access this page.")
        login_page()


if __name__ == "__main__":
    main()
