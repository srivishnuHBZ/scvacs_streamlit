import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from app.database import get_total_vehicles_today, get_unauthorized_attempts, get_guest_passes_issued, get_peak_hour_traffic, get_vehicle_trends, get_hourly_distribution, get_todays_vehicle_history, get_todays_guests

def create_trend_chart(df):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_vehicles'],
        name='Total Vehicles',
        line=dict(color='#2E86C1', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['authorized'],
        name='Authorized',
        line=dict(color='#27AE60', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['unauthorized'],
        name='Unauthorized',
        line=dict(color='#E74C3C', width=2)
    ))
    
    fig.update_layout(
        title='Vehicle Access Trends (Last 7 Days)',
        xaxis_title='Date',
        yaxis_title='Number of Vehicles',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_hourly_distribution_chart(df):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['hour'],
        y=df['count'],
        marker_color='#3498DB'
    ))
    
    fig.update_layout(
        title='Hourly Traffic Distribution (Today)',
        xaxis_title='Hour of Day',
        yaxis_title='Number of Vehicles',
        template='plotly_white',
        xaxis=dict(tickmode='array', ticktext=[f'{i:02d}:00' for i in range(24)], tickvals=list(range(24))),
        height=400
    )
    
    return fig

def generate_excel_report(trends_data, hourly_data, vehicle_history, guests_data):
    # Create Excel writer object
    output = pd.ExcelWriter('scvacs_vehicle_report.xlsx', engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet
    trends_data.to_excel(output, sheet_name='Weekly Trends', index=False)
    hourly_data.to_excel(output, sheet_name='Hourly Distribution', index=False)
    vehicle_history.to_excel(output, sheet_name='Today Vehicle History', index=False)

    # Sort guests by approval status (Approved first)
    guests_data = guests_data.sort_values(by='status', ascending=False)

    # Write guest data to sheet
    guests_data.to_excel(output, sheet_name='Today Guests', index=False)

    # Apply formatting
    workbook = output.book
    worksheet = output.sheets['Today Guests']

    # Define formats
    approved_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})  # Green
    rejected_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})  # Red

    # Get the status column index
    status_col_idx = guests_data.columns.get_loc('status') + 1  # 1-based index

    # Apply conditional formatting
    worksheet.conditional_format(1, status_col_idx, len(guests_data), status_col_idx, 
                                 {'type': 'text', 'criteria': 'containing', 'value': 'Approved', 'format': approved_format})
    worksheet.conditional_format(1, status_col_idx, len(guests_data), status_col_idx, 
                                 {'type': 'text', 'criteria': 'containing', 'value': 'Rejected', 'format': rejected_format})

    # Auto-adjust column widths
    for i, col in enumerate(guests_data.columns):
        max_len = max(guests_data[col].astype(str).apply(len).max(), len(col)) + 2
        worksheet.set_column(i, i, max_len)

    output.close()
    
    with open('scvacs_vehicle_report.xlsx', 'rb') as f:
        return f.read()


def render_page():
    st.title("📊 Analytics Dashboard")
    
    # Auto refresh every 30 seconds
    st_autorefresh(interval=30000, key="analytics_refresh")
    
    try:
        from app.database import engine
        
        with engine.connect() as conn:
            # Metrics Row with cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                with st.container(border=True):
                    st.markdown("### 🚗 Total Vehicles")
                    value = get_total_vehicles_today(conn)
                    st.markdown(f"## {value}")
            
            with col2:
                with st.container(border=True):
                    st.markdown("### ⚠️ Unauthorized")
                    value = get_unauthorized_attempts(conn)
                    st.markdown(f"## {value}")
            
            with col3:
                with st.container(border=True):
                    st.markdown("### 📝 Guest Passes")
                    value = get_guest_passes_issued(conn)
                    st.markdown(f"## {value}")
            
            with col4:
                with st.container(border=True):
                    st.markdown("### ⏰ Peak Hour")
                    value = get_peak_hour_traffic(conn)
                    st.markdown(f"## {value}")
            
         
            col1, col2 = st.columns(2)
            
            # Vehicle trends over time
            trends_data = get_vehicle_trends(conn)
            trend_chart = create_trend_chart(trends_data)
            col1.plotly_chart(trend_chart, use_container_width=True)
            
            # Hourly distribution
            hourly_data = get_hourly_distribution(conn)
            hourly_chart = create_hourly_distribution_chart(hourly_data)
            col2.plotly_chart(hourly_chart, use_container_width=True)
            
            # Get data for tables and download
            vehicle_history = get_todays_vehicle_history(conn)
            guests_data = get_todays_guests(conn)
            
            # Download button
            excel_data = generate_excel_report(trends_data, hourly_data, vehicle_history, guests_data)
            st.download_button(
                label="📥 Download Complete Report",
                data=excel_data,
                file_name=f"scvacs_vehicle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.ms-excel",
            )
                        
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

if __name__ == "__main__":
    render_page()