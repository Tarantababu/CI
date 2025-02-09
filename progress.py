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

def progress_page():
    # Page Title
    st.title("📊 Daily Goal")

    # Daily Goal Section
    st.header("🎯 0/15 min")
    st.markdown("---")

    # Watch Section
    st.subheader("📺 Watch")
    col1, col2, col3, col4 = st.columns(4)
    col1.button("🎬 Series")
    col2.button("📚 Library")
    col3.button("📈 Progress")
    col4.button("💎 Try Premium")

    # Fetch Daily Target from Database
    user_id = 1  # Replace with the actual user ID
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    target = c.execute("SELECT target_minutes FROM user_targets WHERE user_id = ? ORDER BY set_date DESC LIMIT 1",
                       (user_id,)).fetchone()
    conn.close()

    if target:
        st.write(f"**Daily Target:** 🕒 {target[0]} minutes")
    else:
        st.write("**Daily Target:** 🕒 Not set")

    # Fetch User Progress
    conn = sqlite3.connect('german_videos.db')
    c = conn.cursor()
    progress = c.execute("SELECT SUM(duration) FROM user_progress WHERE user_id = ? AND watched_date = ?",
                         (user_id, datetime.now().date())).fetchone()[0] or 0
    conn.close()

    # Progress Bar
    if target:
        progress_percent = min((progress / target[0]) * 100, 100)
        st.progress(int(progress_percent))
        st.write(f"**Total minutes watched today:** 🕒 {progress} / {target[0]} minutes")
    else:
        st.write(f"**Total minutes watched today:** 🕒 {progress} minutes")

    # Level Details
    levels = [
        {
            "level": "Level 1",
            "description": "Starting from zero.",
            "hours": 0,
            "known_words": 0,
            "days_to_reach": 0
        },
        {
            "level": "Level 2",
            "description": "You know some common words.",
            "hours": 50,
            "known_words": 300,
            "days_to_reach": 200
        },
        {
            "level": "Level 3",
            "description": "You can follow topics that are adapted for learners.",
            "hours": 150,
            "known_words": 1500,
            "days_to_reach": 600
        },
        {
            "level": "Level 4",
            "description": "You can understand a person speaking to you patiently.",
            "hours": 300,
            "known_words": 3000,
            "days_to_reach": 1200
        },
        {
            "level": "Level 5",
            "description": "You can understand native speakers speaking to you normally.",
            "hours": 600,
            "known_words": 5000,
            "days_to_reach": 2400
        },
        {
            "level": "Level 6",
            "description": "You are comfortable with daily conversation.",
            "hours": 1000,
            "known_words": 7000,
            "days_to_reach": 4000
        },
        {
            "level": "Level 7",
            "description": "You can use the language effectively for all practical purposes.",
            "hours": 1500,
            "known_words": 12000,
            "days_to_reach": 6000
        }
    ]

    # Display Current Level
    current_level = levels[0]  # Assuming the user is at Level 1
    st.subheader(f"🌟 {current_level['level']}")
    st.write(current_level["description"])
    st.metric("Hours of input", f"{current_level['hours']} hours")
    st.metric("Known words", f"{current_level['known_words']} words")

    # Display Next Level
    if len(levels) > 1:
        next_level = levels[1]
        st.subheader(f"🚀 Next Level: {next_level['level']}")
        st.write(next_level["description"])
        st.metric("Hours to next level", f"{next_level['hours'] - current_level['hours']} hours")
        st.write(f"**You'll reach this level in {next_level['days_to_reach']} days based on your current daily goal.**")

    # Your Activity Section
    st.subheader("📅 Your activity")
    st.write("Current streak: Reach a max streak of 7 by practicing every day.")

    # Calendar Section
    st.subheader("📅 February - 2025")
    st.write("5 M T W T F S")

    # Calendar Table
    calendar_data = {
        "Week in a row": ["10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
        " ": ["23", "24", "25", "26", "27", "28", "", "", "", "", "", ""]
    }
    st.table(calendar_data)

    # Outside Hours Section
    st.subheader("🌍 Outside hours")
    st.write("hours outside the platform")
