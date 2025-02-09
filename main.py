# main.py
import streamlit as st
import sqlite3
import hashlib
import datetime
import re
from datetime import date

class Database:
    def __init__(self, db_name='german_learning.db'):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    daily_target INTEGER DEFAULT 30
                )
            ''')
            
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
            
            # Create admin user if it doesn't exist
            c.execute("SELECT * FROM users WHERE username = 'admin'")
            if not c.fetchone():
                from services import UserService
                UserService().create_user('admin', 'admin123', is_admin=True)

class UserService:
    def __init__(self):
        self.db = Database()

    def hash_password(self, password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    def create_user(self, username, password, is_admin=False):
        with self.db.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                    (username, self.hash_password(password), is_admin)
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def verify_user(self, username, password):
        with self.db.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user = c.fetchone()
            if user and self.hash_password(password) == user[2]:
                return user
            return None

    def update_daily_target(self, user_id, target):
        with self.db.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET daily_target = ? WHERE id = ?", 
                     (target, user_id))
            return True

    def get_daily_target(self, user_id):
        with self.db.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT daily_target FROM users WHERE id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else 30

class VideoService:
    def __init__(self):
        self.db = Database()

    def extract_youtube_id(self, url):
        pattern = r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/\s]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def add_video(self, title, youtube_url, level, tags, duration):
        youtube_id = self.extract_youtube_id(youtube_url)
        if not youtube_id:
            return False
            
        with self.db.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO videos (title, youtube_id, level, tags, duration) VALUES (?, ?, ?, ?, ?)",
                    (title, youtube_id, level, tags, duration)
                )
                return True
            except Exception:
                return False

    def get_videos(self, level=None, tag=None):
        with self.db.get_connection() as conn:
            c = conn.cursor()
            
            query = "SELECT * FROM videos"
            params = []
            
            if level or tag:
                query += " WHERE "
                conditions = []
                if level and level != "All":
                    conditions.append("level = ?")
                    params.append(level)
                if tag:
                    conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
                if conditions:
                    query += " AND ".join(conditions)
            
            c.execute(query, params)
            return c.fetchall()

class ProgressService:
    def __init__(self):
        self.db = Database()

    def log_watch(self, user_id, video_id):
        with self.db.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO watch_history (user_id, video_id, watched_date) VALUES (?, ?, ?)",
                    (user_id, video_id, date.today())
                )
                return True
            except Exception:
                return False

    def get_daily_progress(self, user_id, date_=None):
        if not date_:
            date_ = date.today()
        
        with self.db.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT SUM(v.duration)
                FROM watch_history wh
                JOIN videos v ON wh.video_id = v.id
                WHERE wh.user_id = ? AND wh.watched_date = ?
            """, (user_id, date_))
            
            result = c.fetchone()[0]
            return result if result else 0

def main():
    st.set_page_config(page_title="German Learning Platform", layout="wide")
    
    # Initialize services
    db = Database()
    db.init_db()
    user_service = UserService()
    video_service = VideoService()
    progress_service = ProgressService()
    
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
                user = user_service.verify_user(username, password)
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
                if user_service.create_user(new_username, new_password):
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
                if video_service.add_video(title, youtube_url, level, tags, duration):
                    st.success("Video added successfully!")
                else:
                    st.error("Error adding video")
        
        elif page == "Browse Videos":
            st.header("Browse Videos")
            
            col1, col2 = st.columns(2)
            with col1:
                level_filter = st.selectbox("Filter by Level", ["All", "Beginner", "Intermediate", "Advanced"])
            with col2:
                tag_filter = st.text_input("Filter by Tag")
            
            videos = video_service.get_videos(
                level=level_filter,
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
                            if progress_service.log_watch(st.session_state.user[0], video[0]):
                                st.success("Progress logged!")
                    st.video(f"https://youtube.com/watch?v={video[2]}")
        
        elif page == "Progress Tracking":
            st.header("Progress Tracking")
            
            daily_target = user_service.get_daily_target(st.session_state.user[0])
            new_target = st.number_input("Daily Target (minutes)", value=daily_target)
            
            if new_target != daily_target:
                user_service.update_daily_target(st.session_state.user[0], new_target)
            
            today_progress = progress_service.get_daily_progress(st.session_state.user[0])
            progress_percentage = (today_progress / new_target) * 100 if new_target > 0 else 0
            
            st.metric(
                "Today's Progress",
                f"{today_progress} minutes",
                delta=f"{new_target - today_progress} minutes to goal"
            )
            st.progress(min(progress_percentage / 100, 1.0))

if __name__ == "__main__":
    main()
