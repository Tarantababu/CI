import streamlit as st

# Import pages
from progress import progress_page
from dashboard import dashboard_page

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Progress"])

# Display the selected page
if page == "Dashboard":
    dashboard_page()
elif page == "Progress":
    progress_page()
