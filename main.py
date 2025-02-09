import streamlit as st
from progress import progress_page
from dashboard import dashboard_page
from admin import admin_panel

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
