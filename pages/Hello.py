import streamlit as st

st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide")
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Home","Live Matches","Top Player Stats","SQL Queries & Analytics","CRUD","About"])

if menu == "Home":
    st.title("🏏 Cricbuzz LiveStats — Home")
    st.write("""
        This project integrates the RapidAPI Cricbuzz endpoints with a local **SQLite** database to provide:
        - Real-time live matches page (fetches from RapidAPI)
        - Top player stats page (fetches from RapidAPI)
        - SQL Queries & Analytics (25 queries implemented using Mysql and fetches from RapidAPI)
        - CRUD operations to manage players & matches
        """)

if menu == "Live Matches":
    st.title("🏏 Cricbuzz LiveStats — Live, Recent and Upcoming Matches")   
    pg_live = st.navigation([
        st.Page("1_live_matches.py", title="Live Matches Page", icon="🔥")
    ])
    pg_live.run()

if menu == "Top Player Stats":
    st.title("🏏 Cricbuzz LiveStats — Top Player Stats")  
    pg_stats = st.navigation([
        st.Page("2_top_stats.py", title="Top Player Stats Page", icon="🔥")
    ])
    pg_stats.run()
    
if menu == "SQL Queries & Analytics":
    pg_sql_queries = st.navigation([
        st.Page("3_sql_queries.py", title="First page", icon="🔥")
    ])
    pg_sql_queries.run()

if menu == "CRUD":
    pg_crud = st.navigation([
        st.Page("4_crud_operations.py", title="First page", icon="🔥")
    ])
    pg_crud.run()

if menu == "About":
    st.text("This Project is created by Poorvaj Naresh S P using Streamlit with Python and SQL")

    
