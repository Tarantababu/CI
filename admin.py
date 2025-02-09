import streamlit as st
import sqlite3
from datetime import datetime

def admin_panel():
    st.sidebar.header("Admin Panel")

    # Add Video Section
    st.sidebar.subheader("Add New Video")
    title = st.sidebar.text_input("Title")
    level = st.sidebar.selectbox("Level", ["Superbeginner", "Beginner", "Intermediate", "Advanced"])
    url = st.sidebar.text_input("YouTube URL")
    tags = st.sidebar.text_input("Tags (comma separated)")
    add_button = st.sidebar.button("Add Video")

    if add_button:
        if title and level and url:
            conn = sqlite3.connect('german_videos.db')
            c = conn.cursor()
            c.execute("INSERT INTO videos (title, level, url, tags, added_date) VALUES (?, ?, ?, ?, ?)",
                      (title, level, url, tags, datetime.now().date()))
            conn.commit()
            conn.close()
            st.sidebar.success("Video added successfully!")
        else:
            st.sidebar.error("Please fill in all fields.")

    # Set Daily Target Section
    st.sidebar.subheader("Set Daily Target for Users")
    user_id = st.sidebar.number_input("User ID", min_value=1, value=1)
    target_minutes = st.sidebar.number_input("Daily Target (minutes)", min_value=1, value=30)
    set_target_button = st.sidebar.button("Set Target")

    if set_target_button:
        conn = sqlite3.connect('german_videos.db')
        c = conn.cursor()
        c.execute("INSERT INTO user_targets (user_id, target_minutes, set_date) VALUES (?, ?, ?)",
                  (user_id, target_minutes, datetime.now().date()))
        conn.commit()
        conn.close()
        st.sidebar.success("Daily target set successfully!")
