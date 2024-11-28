import streamlit as st
import pyodbc
import pandas as pd
import time
from datetime import datetime, timedelta

# Function to fetch data from the Azure SQL Database
def fetch_vehicle_history():
    server = 'vnpr.database.windows.net,1433'
    database = 'vnpr'
    username = 'vnpradmin'
    password = 'Vnpr@1234'

    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout=30;"
    )

    try:
        conn = pyodbc.connect(connection_string)
        query = "SELECT TOP 100 * FROM VEHICLE_HISTORY ORDER BY ID DESC;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error: {e}"

# Function to display the login page
def login_page():
    st.markdown(
        """
        <style>
        .login-box {
            width: 400px;
            margin: auto;
            padding: 30px;
            border-radius: 10px;
            background-color: white;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        .login-title {
            text-align: center;
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
            font-weight: bold;
        }
        </style>
        <div class="login-box">
            <div class="login-title">SMART CAMPUS VEHICLE ACCESS CONTROL SYSTEM</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    if st.button("Login"):
        if username == "admin" and password == "admin":  # Replace with real authentication logic
            st.session_state.logged_in = True
            # Show the success message only for a moment
            st.success("Login successful! Redirecting...")
            time.sleep(1)  # Short pause for user feedback
            st.rerun()
        else:
            st.error("Invalid username or password.")

# Function to display the main application
def main_app():
    st.title("SMART CAMPUS VEHICLE ACCESS CONTROL SYSTEM")
    st.write("### Vehicle History Data")

    # # Logout button
    # if st.button("Logout"):
    #     st.session_state.logged_in = False
    #     st.rerun()

    # Create two columns for filtering options
    col1, col2 = st.columns(2)

    with col1:
        plate_number_filter = st.text_input("Search by Plate Number:", placeholder="Enter plate number...")

    with col2:
        date_range = st.date_input(
            "Select Date Range:",
            value=(datetime.now() - timedelta(days=7), datetime.now()),  # Default to last 7 days
            help="Filter results by a specific date range.",
        )

    # Validate the selected date range
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        st.error("Please select a valid start and end date.")
        return

    # Create a placeholder for the table
    table_placeholder = st.empty()

    # Infinite loop to refresh data
    while True:
        # Fetch the data from the database
        data = fetch_vehicle_history()

        # Check if data is a DataFrame before checking if it's empty
        if isinstance(data, pd.DataFrame):
            if not data.empty:
                # Apply filtering based on the plate number
                if plate_number_filter:
                    data = data[data['Plate_Number'].str.contains(plate_number_filter, case=False, na=False)]

                # Apply filtering based on the selected date range
                if not data.empty:
                    data['Stamp'] = pd.to_datetime(data['Stamp'])  # Ensure 'Stamp' column is in datetime format
                    # Adjust end_date to include the entire day
                    adjusted_end_date = end_date + timedelta(days=1)
                    data = data[(data['Stamp'] >= pd.to_datetime(start_date)) & (data['Stamp'] < pd.to_datetime(adjusted_end_date))]

                # Display the filtered data in the placeholder
                table_placeholder.dataframe(data, use_container_width=True)
            else:
                st.warning("No data available.")
        else:
            st.error(data)  # Handle the case where data is not a DataFrame

        # Refresh interval
        start_time = time.time()
        elapsed_time = time.time() - start_time
        sleep_time = max(0.1, 1 - elapsed_time)
        time.sleep(sleep_time)

        
# Main function to control navigation between login and main application
def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()
        

# Run the application
if __name__ == "__main__":
    main()
