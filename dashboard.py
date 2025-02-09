import streamlit as st

def dashboard_page():
    # Page Title
    st.title("Daily Goal")

    # Search Section
    st.subheader("Search")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.button("Watch")
    col2.button("Series")
    col3.button("Library")
    col4.button("Progress")
    col5.button("Try Premium")

    st.markdown("---")

    # Video Library Section
    st.subheader("2127 videos found (491 premium). Duration: 427h 14m.")

    # Example Videos
    st.write("**The Reddit Advice Show with Andrea & Michelle En. 2**")
    st.write("**The Reddit Advice Show with Andrea & Michelle En. 1**")
    st.write("**Café Comments & Street Stall with the Arons of Coffee and Vinyl Tunes**")
    st.write("**Tapovich El Callin de Leder Michelle-Star-Worthy Street Food?**")

    # Premium Content Section
    st.subheader("JUNG “ORPASS”")
    st.write("Find Your Way: How to Use a Map and Compass Effectively")
    st.write("[Admitted]")

    st.subheader("FINALLY WELLER")
    st.write("We Finally Met... In Sevillet")
    st.write("[Admitted]")

    st.subheader("INTO THE WILD")
