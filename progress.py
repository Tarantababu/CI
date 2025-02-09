import streamlit as st

def progress_page():
    # Page Title
    st.title("Daily Goal")

    # Daily Goal Section
    st.header("0/15 min")
    st.markdown("---")

    # Watch Section
    st.subheader("Watch")
    col1, col2, col3, col4 = st.columns(4)
    col1.button("Series")
    col2.button("Library")
    col3.button("Progress")
    col4.button("Try Premium")

    # Overall Progression Section
    st.subheader("Overall progression")
    st.write("You are currently in Level 1")

    col1, col2 = st.columns(2)
    col1.metric("Total input time", "0 min")
    col2.metric("0 hr", "50 hrs")

    st.metric("Hours to level 2", "50 hrs")

    # Your Activity Section
    st.subheader("Your activity")
    st.write("Current streak: Reach a max streak of 7 by practicing every day.")

    # Calendar Section
    st.subheader("February - 2025")
    st.write("5 M T W T F S")

    # Calendar Table
    calendar_data = {
        "Week in a row": ["10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
        " ": ["23", "24", "25", "26", "27", "28", "", "", "", "", "", ""]
    }
    st.table(calendar_data)

    # Outside Hours Section
    st.subheader("Outside hours")
    st.write("hours outside the platform")
