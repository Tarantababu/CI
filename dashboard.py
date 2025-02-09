import streamlit as st
import sqlite3

def dashboard_page():
    # Page Title
    st.title("German Learning Videos")

    # Search Section
    st.subheader("Search")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.button("Watch")
    col2.button("Series")
    col3.button("Library")
    col4.button("Progress")
    col5.button("Try Premium")

    st.markdown("---")

    # Fetch Videos from Database
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    videos = c.execute("SELECT * FROM videos").fetchall()
    conn.close()

    # Display Videos
    st.subheader(f"{len(videos)} videos found")
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
