import streamlit as st
import pandas as pd
import datetime
import sqlite3
import hashlib
from datetime import timedelta
import yaml
import re

# Initialize database
def init_db():
    conn = sqlite3.connect('german_learning.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            daily_target INTEGER DEFAULT 30
        )
    ''')
    
    # Create videos table
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            youtube_id TEXT NOT NULL,
            level TEXT NOT NULL,
            tags TEXT,
            duration INTEGER NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create watch_history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS watch_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            video_id INTEGER,
            watched_date DATE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Security functions
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_password(password, hashed_password):
    return hash_password(password) == hashed_password

# User management
def create_user(username, password, is_admin=False):
    conn = sqlite3.connect('german_learning.db')
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (username, hash_password(password), is_admin)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('german_learning.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password(password, user[2]):
        return user
    return None

# Video management
def extract_youtube_id(url):
    pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def add_video(title, youtube_url, level, tags, duration):
    youtube_id = extract_youtube_id(youtube_url)
    if not youtube_id:
        return False
        
    conn = sqlite3.connect('german_learning.db')
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO videos (title, youtube_id, level, tags, duration) VALUES (?, ?, ?, ?, ?)",
            (title, youtube_id, level, tags, duration)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding video: {e}")
        return False
    finally:
        conn.close()

def get_videos(level=None, tag=None):
    conn = sqlite3.connect('german_learning.db')
    c = conn.cursor()
    
    query = "SELECT * FROM videos"
    params = []
    
    if level or tag:
        query += " WHERE "
        conditions = []
        if level:
            conditions.append("level = ?")
            params.append(level)
        if tag:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")
        query += " AND ".join(conditions)
    
    c.execute(query, params)
    videos = c.fetchall()
    conn.close()
    return videos

# Progress tracking
def log_watch(user_id, video_id):
    conn = sqlite3.connect('german_learning.db')
    c = conn.cursor()
    today = datetime.date.today()
    try:
        c.execute(
            "INSERT INTO watch_history (user_id, video_id, watched_date) VALUES (?, ?, ?)",
            (user_id, video_id, today)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error logging watch: {e}")
        return False
    finally:
        conn.close()

def get_daily_progress(user_id, date=None):
    if not date:
        date = datetime.date.today()
    
    conn = sqlite3.connect('german_learning.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT SUM(v.duration)
        FROM watch_history wh
        JOIN videos v ON wh.video_id = v.id
        WHERE wh.user_id = ? AND wh.watched_date = ?
    """, (user_id, date))
    
    result = c.fetchone()[0]
    conn.close()
    return result if result else 0

# Streamlit UI
def main():
    st.set_page_config(page_title="German Learning Platform", layout="wide")
    
    # Initialize database
    init_db()
    
    # Session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Login/Register UI
    if not st.session_state.user:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.header("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user = verify_user(username, password)
                if user:
                    st.session_state.user = user
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            st.header("Register")
            new_username = st.text_input("Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")
            if st.button("Register"):
                if create_user(new_username, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")
    
    else:
        # Main application UI
        st.sidebar.title("Navigation")
        if st.session_state.user[3]:  # is_admin
            page = st.sidebar.radio("Go to", ["Browse Videos", "Add Video", "Admin Dashboard"])
        else:
            page = st.sidebar.radio("Go to", ["Browse Videos", "Progress Tracking"])
        
        st.sidebar.button("Logout", on_click=lambda: setattr(st.session_state, 'user', None))
        
        if page == "Add Video" and st.session_state.user[3]:
            st.header("Add New Video")
            title = st.text_input("Video Title")
            youtube_url = st.text_input("YouTube URL")
            level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
            tags = st.text_input("Tags (comma-separated)")
            duration = st.number_input("Duration (minutes)", min_value=1)
            
            if st.button("Add Video"):
                if add_video(title, youtube_url, level, tags, duration):
                    st.success("Video added successfully!")
                else:
                    st.error("Error adding video")
        
        elif page == "Browse Videos":
            st.header("Browse Videos")
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                level_filter = st.selectbox("Filter by Level", ["All", "Beginner", "Intermediate", "Advanced"])
            with col2:
                tag_filter = st.text_input("Filter by Tag")
            
            # Get and display videos
            videos = get_videos(
                level=None if level_filter == "All" else level_filter,
                tag=tag_filter if tag_filter else None
            )
            
            for video in videos:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(video[1])
                        st.write(f"Level: {video[3]}")
                        st.write(f"Tags: {video[4]}")
                    with col2:
                        if st.button("Mark as Watched", key=f"watch_{video[0]}"):
                            if log_watch(st.session_state.user[0], video[0]):
                                st.success("Progress logged!")
                    st.video(f"https://youtube.com/watch?v={video[2]}")
        
        elif page == "Progress Tracking":
            st.header("Progress Tracking")
            
            # Get daily target
            conn = sqlite3.connect('german_learning.db')
            c = conn.cursor()
            c.execute("SELECT daily_target FROM users WHERE id = ?", (st.session_state.user[0],))
            daily_target = c.fetchone()[0]
            conn.close()
            
            # Update daily target
            new_target = st.number_input("Daily Target (minutes)", value=daily_target)
            if new_target != daily_target:
                conn = sqlite3.connect('german_learning.db')
                c = conn.cursor()
                c.execute("UPDATE users SET daily_target = ? WHERE id = ?", 
                         (new_target, st.session_state.user[0]))
                conn.commit()
                conn.close()
            
            # Show today's progress
            today_progress = get_daily_progress(st.session_state.user[0])
            progress_percentage = (today_progress / new_target) * 100 if new_target > 0 else 0
            
            st.metric(
                label="Today's Progress",
                value=f"{today_progress} minutes",
                delta=f"{new_target - today_progress} minutes to goal"
            )
            
            st.progress(min(progress_percentage / 100, 1.0))

if __name__ == "__main__":
    main()
