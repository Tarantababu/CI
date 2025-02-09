import streamlit as st
from progress import progress_page
from dashboard import dashboard_page

# Admin Panel Functionality
def admin_panel():
    st.sidebar.header("Admin Panel")
    st.sidebar.subheader("Set Daily Target for Users")

    # Input for setting daily target
    user_id = st.sidebar.number_input("User ID", min_value=1, value=1)
    target_minutes = st.sidebar.number_input("Daily Target (minutes)", min_value=1, value=30)
    set_target_button = st.sidebar.button("Set Target")

    if set_target_button:
        # Save the target to the database (or any storage)
        # Example: Save to SQLite database
        import sqlite3
        conn = sqlite3.connect('german_videos.db')
        c = conn.cursor()
        c.execute("INSERT INTO user_targets (user_id, target_minutes, set_date) VALUES (?, ?, ?)",
                  (user_id, target_minutes, datetime.now().date()))
        conn.commit()
        conn.close()
        st.sidebar.success("Daily target set successfully!")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Progress"])

# Admin Panel Checkbox
is_admin = st.sidebar.checkbox("Admin Mode")

# Display the selected page
if page == "Dashboard":
    dashboard_page()
elif page == "Progress":
    progress_page()

# Show Admin Panel if in Admin Mode
if is_admin:
    admin_panel()
