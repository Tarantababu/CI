import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# Database setup
conn = sqlite3.connect('german_videos.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS videos
             (id INTEGER PRIMARY KEY, title TEXT, level TEXT, url TEXT, tags TEXT, added_date DATE)''')

c.execute('''CREATE TABLE IF NOT EXISTS user_progress
             (id INTEGER PRIMARY KEY, user_id INTEGER, video_id INTEGER, watched_date DATE, duration INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS user_targets
             (id INTEGER PRIMARY KEY, user_id INTEGER, target_minutes INTEGER, set_date DATE)''')

conn.commit()

# Streamlit app
st.title("German Learning Videos")

# Sidebar for admin to add videos
st.sidebar.header("Admin Panel")
st.sidebar.subheader("Add New Video")

title = st.sidebar.text_input("Title")
level = st.sidebar.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
url = st.sidebar.text_input("YouTube URL")
tags = st.sidebar.text_input("Tags (comma separated)")
add_button = st.sidebar.button("Add Video")

if add_button:
    if title and level and url:
        c.execute("INSERT INTO videos (title, level, url, tags, added_date) VALUES (?, ?, ?, ?, ?)",
                  (title, level, url, tags, datetime.now().date()))
        conn.commit()
        st.sidebar.success("Video added successfully!")
    else:
        st.sidebar.error("Please fill in all fields.")

# Main content
st.header("Browse Videos")

# Filter videos by level and tags
levels = ["Beginner", "Intermediate", "Advanced"]
selected_level = st.selectbox("Select Level", levels)
selected_tags = st.text_input("Filter by Tags (comma separated)")

query = "SELECT * FROM videos WHERE level = ?"
params = [selected_level]

if selected_tags:
    tags_list = [tag.strip() for tag in selected_tags.split(",")]
    query += " AND ("
    for i, tag in enumerate(tags_list):
        query += "tags LIKE ?"
        params.append(f"%{tag}%")
        if i < len(tags_list) - 1:
            query += " OR "
    query += ")"

videos = c.execute(query, params).fetchall()

if videos:
    for video in videos:
        st.subheader(video[1])
        st.video(video[3])
        st.write(f"Level: {video[2]}")
        st.write(f"Tags: {video[4]}")
        st.write(f"Added on: {video[5]}")
        if st.button(f"Mark as Watched - {video[1]}", key=video[0]):
            c.execute("INSERT INTO user_progress (user_id, video_id, watched_date, duration) VALUES (?, ?, ?, ?)",
                      (1, video[0], datetime.now().date(), 10))  # Assuming 10 minutes per video
            conn.commit()
            st.success("Video marked as watched!")
else:
    st.write("No videos found for the selected filters.")

# User progress tracking
st.header("Your Progress")

# Set daily target
st.subheader("Set Daily Target")
target_minutes = st.number_input("Enter your daily target in minutes", min_value=1, value=30)
set_target_button = st.button("Set Target")

if set_target_button:
    c.execute("INSERT INTO user_targets (user_id, target_minutes, set_date) VALUES (?, ?, ?)",
              (1, target_minutes, datetime.now().date()))
    conn.commit()
    st.success("Daily target set successfully!")

# Display progress
st.subheader("Daily Consumption")
progress = c.execute("SELECT SUM(duration) FROM user_progress WHERE user_id = ? AND watched_date = ?",
                     (1, datetime.now().date())).fetchone()[0] or 0
st.write(f"Total minutes watched today: {progress}")

target = c.execute("SELECT target_minutes FROM user_targets WHERE user_id = ? ORDER BY set_date DESC LIMIT 1",
                   (1,)).fetchone()
if target:
    target_minutes = target[0]
    st.write(f"Daily target: {target_minutes} minutes")
    if progress >= target_minutes:
        st.success("You've reached your daily target!")
    else:
        st.warning(f"You need to watch {target_minutes - progress} more minutes to reach your target.")

# Close the database connection
conn.close()
