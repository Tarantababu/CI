import streamlit as st
import sqlite3
from datetime import datetime

# Custom CSS for modern design
st.markdown(
    """
    <style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #4CAF50;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stTable {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize the database
def init_db():
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
    conn.close()

# Fetch videos from the database
def fetch_videos():
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos")
    videos = c.fetchall()
    conn.close()
    return videos

# Add a new video to the database
def add_video(title, level, url, tags):
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    c.execute("INSERT INTO videos (title, level, url, tags, added_date) VALUES (?, ?, ?, ?, ?)",
              (title, level, url, tags, datetime.now().date()))
    conn.commit()
    conn.close()

# Fetch user progress from the database
def fetch_user_progress(user_id):
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    c.execute("SELECT SUM(duration) FROM user_progress WHERE user_id = ? AND watched_date = ?",
              (user_id, datetime.now().date()))
    progress = c.fetchone()[0] or 0
    conn.close()
    return progress

# Fetch daily target from the database
def fetch_daily_target(user_id):
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    c.execute("SELECT target_minutes FROM user_targets WHERE user_id = ? ORDER BY set_date DESC LIMIT 1",
              (user_id,))
    target = c.fetchone()
    conn.close()
    return target[0] if target else None

# Set daily target for a user
def set_daily_target(user_id, target_minutes):
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_targets (user_id, target_minutes, set_date) VALUES (?, ?, ?)",
              (user_id, target_minutes, datetime.now().date()))
    conn.commit()
    conn.close()

# Update hours spent
def update_hours_spent(user_id, hours_spent):
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_progress (user_id, video_id, watched_date, duration) VALUES (?, ?, ?, ?)",
              (user_id, 0, datetime.now().date(), hours_spent * 60))  # Convert hours to minutes
    conn.commit()
    conn.close()

# Progress Page
def progress_page():
    st.title("📊 Daily Goal")
    
    # Fetch user data
    user_id = 1  # Replace with the actual user ID
    progress_minutes = fetch_user_progress(user_id)
    progress_hours = progress_minutes / 60
    daily_target = fetch_daily_target(user_id)
    
    # Overall Progression Section
    st.header("Overall progression")
    st.write("You are currently in **Level 1**")
    
    col1, col2 = st.columns(2)
    col1.metric("Total input time", f"{int(progress_hours)} hr")
    col2.metric("Hours to level 2", f"{50 - int(progress_hours)} hr")
    
    # Level Details
    levels = [
        {"level": "Level 1", "description": "Starting from zero.", "hours": 0, "known_words": 0, "days_to_reach": 0},
        {"level": "Level 2", "description": "You know some common words.", "hours": 50, "known_words": 300, "days_to_reach": 200},
        {"level": "Level 3", "description": "You can follow topics that are adapted for learners.", "hours": 150, "known_words": 1500, "days_to_reach": 600},
        {"level": "Level 4", "description": "You can understand a person speaking to you patiently.", "hours": 300, "known_words": 3000, "days_to_reach": 1200},
        {"level": "Level 5", "description": "You can understand native speakers speaking to you normally.", "hours": 600, "known_words": 5000, "days_to_reach": 2400},
        {"level": "Level 6", "description": "You are comfortable with daily conversation.", "hours": 1000, "known_words": 7000, "days_to_reach": 4000},
        {"level": "Level 7", "description": "You can use the language effectively for all practical purposes.", "hours": 1500, "known_words": 12000, "days_to_reach": 6000}
    ]
    
    # Display Current Level
    current_level = levels[0]  # Assuming the user is at Level 1
    st.subheader(f"🌟 {current_level['level']}")
    st.write(current_level["description"])
    st.metric("Hours of input", f"{int(progress_hours)} hours")
    st.metric("Known words", f"{current_level['known_words']} words")
    
    # Display Next Level
    if len(levels) > 1:
        next_level = levels[1]
        st.subheader(f"🚀 Next Level: {next_level['level']}")
        st.write(next_level["description"])
        hours_to_next_level = next_level["hours"] - progress_hours
        
        # Calculate days to reach the next level
        if daily_target:
            days_to_next_level = hours_to_next_level / (daily_target / 60)  # Convert target minutes to hours
            st.write(f"**You'll reach this level in {int(days_to_next_level)} days based on your current daily goal.**")
        else:
            st.write("**Set a daily target to see how long it will take to reach the next level.**")
    
    # Your Activity Section
    st.header("Your activity")
    st.write("Current streak: Reach a max streak of 7 by practicing every day.")
    
    # Calendar Section
    st.header("February - 2025")
    calendar_data = {
        "S": ["2", "9", "16", "23"],
        "M": ["3", "10", "17", "24"],
        "T": ["4", "11", "18", "25"],
        "W": ["5", "12", "19", "26"],
        "T": ["6", "13", "20", "27"],
        "F": ["7", "14", "21", "28"],
        "S": ["8", "15", "22", ""]
    }
    st.table(calendar_data)
    
    # Edit Hours Spent Section
    st.header("Edit Hours Spent")
    hours_spent = st.number_input("Enter hours spent today", min_value=0, value=0)
    if st.button("Update Hours Spent"):
        update_hours_spent(user_id, hours_spent)
        st.success("Hours spent updated successfully!")

# Admin Panel
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
            add_video(title, level, url, tags)
            st.sidebar.success("Video added successfully!")
        else:
            st.sidebar.error("Please fill in all fields.")
    
    # Set Daily Target Section
    st.sidebar.subheader("Set Daily Target for Users")
    user_id = st.sidebar.number_input("User ID", min_value=1, value=1)
    target_minutes = st.sidebar.number_input("Daily Target (minutes)", min_value=1, value=30)
    set_target_button = st.sidebar.button("Set Target")
    
    if set_target_button:
        set_daily_target(user_id, target_minutes)
        st.sidebar.success("Daily target set successfully!")

# Main App
def main():
    # Initialize the database
    init_db()
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Progress"])
    
    # Admin Panel Checkbox
    is_admin = st.sidebar.checkbox("Admin Mode")
    
    # Display the selected page
    if page == "Dashboard":
        st.title("German Learning Videos")
        videos = fetch_videos()
        for video in videos:
            st.subheader(video[1])  # Title
            st.video(video[3])      # YouTube URL
            st.write(f"**Level:** {video[2]}")  # Level
            st.write(f"**Tags:** {video[4]}")   # Tags
            st.write(f"**Added on:** {video[5]}")  # Added Date
            if st.button(f"Mark as Watched - {video[1]}", key=video[0]):
                conn = sqlite3.connect('german_videos.db')
                c = conn.cursor()
                c.execute("INSERT INTO user_progress (user_id, video_id, watched_date, duration) VALUES (?, ?, ?, ?)",
                          (1, video[0], datetime.now().date(), 10))  # Assuming 10 minutes per video
                conn.commit()
                conn.close()
                st.success("Video marked as watched!")
    elif page == "Progress":
        progress_page()
    
    # Show Admin Panel if in Admin Mode
    if is_admin:
        admin_panel()

if __name__ == "__main__":
    main()
