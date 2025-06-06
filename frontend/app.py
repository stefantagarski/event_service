import streamlit as st
import requests
import json
from datetime import datetime, date
import pandas as pd

import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://event_backend:5000/api")

# Page configuration
st.set_page_config(
    page_title="Event Management System",
    page_icon="🎉",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { 
        font-size: 3rem; 
        color: #1f77b4; 
        text-align: center; 
        margin-bottom: 2rem; 
    }
    .event-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def make_request(method, endpoint, data=None):
    """Make HTTP request to Flask API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)

        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to the server. Make sure Flask API is running."}, 500


def display_event_card(event):
    """Display event in a clean, Streamlit-friendly card format"""
    with st.container():
        # Create a bordered container with modern styling
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, #ffffff, #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                border-left: 4px solid #667eea;
            ">
                <h3 style="
                    color: #1e293b;
                    margin: 0 0 1rem 0;
                    font-size: 1.5rem;
                    font-weight: 600;
                ">{event['title']}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Use Streamlit's native components for better compatibility
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📅 Date:**")
            st.info(f"{event['date']}")

            st.markdown("**👤 Organizer:**")
            st.info(f"{event.get('organizer', 'N/A')}")

        with col2:
            st.markdown("**📍 Location:**")
            st.info(f"{event['location']}")

            st.markdown("**🎫 Capacity:**")
            st.info(f"{event.get('capacity', 'N/A')}")

        st.markdown("**📝 Description:**")
        st.success(f"{event['description']}")

        st.markdown("---")


def create_event_form():
    """Create event form"""
    st.subheader("📝 Create New Event")

    with st.form("create_event_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Event Title*", placeholder="Enter event title")
            date_input = st.date_input("Event Date*", min_value=date.today())
            organizer = st.text_input("Organizer", placeholder="Event organizer name")

        with col2:
            location = st.text_input("Location*", placeholder="Event location")
            capacity = st.number_input("Capacity", min_value=0, value=0)

        description = st.text_area("Description*", placeholder="Event description", height=100)

        submitted = st.form_submit_button("Create Event", type="primary")

        if submitted:
            if not all([title, description, location]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                event_data = {
                    "title": title,
                    "description": description,
                    "date": date_input.strftime("%Y-%m-%d"),
                    "location": location,
                    "organizer": organizer,
                    "capacity": capacity
                }

                response, status_code = make_request("POST", "/events", event_data)

                if status_code == 201:
                    st.success("✅ Event created successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {response.get('error', 'Unknown error')}")


def display_all_events():
    """Display all events"""
    st.subheader("📅 All Events")

    response, status_code = make_request("GET", "/events")

    if status_code == 200:
        events = response.get("events", [])

        if not events:
            st.info("No events found. Create your first event!")
        else:
            # Search functionality
            search_query = st.text_input("🔍 Search events", placeholder="Search by title, description, or location")

            if search_query:
                search_response, search_status = make_request("GET", f"/events/search?q={search_query}")
                if search_status == 200:
                    events = search_response.get("events", [])

            # Display events in a grid
            cols = st.columns(2)
            for i, event in enumerate(events):
                with cols[i % 2]:
                    display_event_card(event)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"✏️ Edit", key=f"edit_{event['_id']}"):
                            st.session_state.edit_event_id = event['_id']
                            st.session_state.show_edit_form = True

                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{event['_id']}"):
                            delete_response, delete_status = make_request("DELETE", f"/events/{event['_id']}")
                            if delete_status == 200:
                                st.success("Event deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Error deleting event: {delete_response.get('error')}")

                    with col3:
                        # Download event as JSON
                        event_json = json.dumps(event, indent=2)
                        st.download_button(
                            "📥 Export",
                            data=event_json,
                            file_name=f"event_{event['_id']}.json",
                            mime="application/json",
                            key=f"download_{event['_id']}"
                        )
    else:
        st.error(f"❌ Error loading events: {response.get('error', 'Unknown error')}")


def edit_event_form():
    """Edit event form"""
    if not st.session_state.get('edit_event_id'):
        return

    event_id = st.session_state.edit_event_id

    # Get event details
    response, status_code = make_request("GET", f"/events/{event_id}")

    if status_code != 200:
        st.error("Event not found")
        return

    event = response['event']

    st.subheader("✏️ Edit Event")

    with st.form("edit_event_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Event Title*", value=event['title'])
            event_date = datetime.strptime(event['date'], "%Y-%m-%d").date()
            date_input = st.date_input("Event Date*", value=event_date, min_value=date.today())
            organizer = st.text_input("Organizer", value=event.get('organizer', ''))

        with col2:
            location = st.text_input("Location*", value=event['location'])
            capacity = st.number_input("Capacity", min_value=0, value=event.get('capacity', 0))

        description = st.text_area("Description*", value=event['description'], height=100)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update Event", type="primary")
        with col2:
            cancelled = st.form_submit_button("Cancel")

        if cancelled:
            st.session_state.show_edit_form = False
            st.session_state.edit_event_id = None
            st.rerun()

        if submitted:
            if not all([title, description, location]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                event_data = {
                    "title": title,
                    "description": description,
                    "date": date_input.strftime("%Y-%m-%d"),
                    "location": location,
                    "organizer": organizer,
                    "capacity": capacity
                }

                response, status_code = make_request("PUT", f"/events/{event_id}", event_data)

                if status_code == 200:
                    st.success("✅ Event updated successfully!")
                    st.session_state.show_edit_form = False
                    st.session_state.edit_event_id = None
                    st.rerun()
                else:
                    st.error(f"❌ Error: {response.get('error', 'Unknown error')}")


def analytics_dashboard():
    """Display analytics dashboard"""
    st.subheader("📊 Analytics Dashboard")

    response, status_code = make_request("GET", "/events")

    if status_code == 200:
        events = response.get("events", [])

        if not events:
            st.info("No events available for analytics.")
            return

        # Convert to DataFrame for analysis
        df = pd.DataFrame(events)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Events", len(events))

        with col2:
            total_capacity = df['capacity'].sum()
            st.metric("Total Capacity", f"{total_capacity:,}")

        with col3:
            avg_capacity = df['capacity'].mean()
            st.metric("Avg Capacity", f"{avg_capacity:.1f}")

        with col4:
            upcoming_events = df[df['date'] >= datetime.now().date()]
            st.metric("Upcoming Events", len(upcoming_events))

        # Charts
        st.subheader("📈 Event Distribution")

        col1, col2 = st.columns(2)

        with col1:
            # Events by month
            monthly_counts = df.groupby('month').size()
            st.bar_chart(monthly_counts)
            st.caption("Events by Month")

        with col2:
            # Top locations
            location_counts = df['location'].value_counts().head(10)
            st.bar_chart(location_counts)
            st.caption("Top Event Locations")

        # Recent events table
        st.subheader("📋 Recent Events")
        recent_events = df.sort_values('created_at', ascending=False).head(10)[
            ['title', 'date', 'location', 'organizer', 'capacity']
        ]
        st.dataframe(recent_events, use_container_width=True)

    else:
        st.error(f"❌ Error loading analytics: {response.get('error', 'Unknown error')}")


def main():
    """Main application"""
    # Initialize session state
    if 'show_edit_form' not in st.session_state:
        st.session_state.show_edit_form = False
    if 'edit_event_id' not in st.session_state:
        st.session_state.edit_event_id = None

    # Header
    st.markdown('<h1 class="main-header">🎉 Event Management System</h1>', unsafe_allow_html=True)

    # Check API connection
    health_response, health_status = make_request("GET", "/health")
    if health_status != 200:
        st.error(
            "⚠️ Cannot connect to the backend API. Please ensure the Flask server is running on http://localhost:5000")
        st.stop()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📝 Create Event", "📅 View Events", "📊 Analytics"]
    )

    # API status
    st.sidebar.success("✅ API Connected")
    st.sidebar.info(f"Status: {health_response.get('status', 'Unknown')}")

    # Main content
    if st.session_state.show_edit_form:
        edit_event_form()
    elif page == "📝 Create Event":
        create_event_form()
    elif page == "📅 View Events":
        display_all_events()
    elif page == "📊 Analytics":
        analytics_dashboard()


if __name__ == "__main__":
    main()
