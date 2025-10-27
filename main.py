import streamlit as st

st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide")

# Import your pages here
import 1_live_matches as live_page
import 2_top_stats as stats_page
import 3_sql_queries as sql_page
import 4_crud_operations as crud_page

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Home","Live Matches","Top Player Stats","SQL Queries & Analytics","CRUD","About"])

# -------------------- HOME PAGE --------------------
if menu == "Home":
    st.title("🏏 Cricbuzz LiveStats Dashboard")
    st.markdown("""
    Welcome to **Cricbuzz LiveStats** — an interactive cricket analytics platform that brings together **live match updates**,  
    **player performance statistics**, **database-driven insights**, and **custom data management tools**, all in one place.
    ---
    """)

# -------------------- LIVE MATCHES PAGE --------------------
elif menu == "Live Matches":
    live_page.live_matches_page()

# -------------------- TOP PLAYER STATS PAGE --------------------
elif menu == "Top Player Stats":
    stats_page.icc_rankings_page()

# -------------------- SQL QUERIES & ANALYTICS PAGE --------------------
elif menu == "SQL Queries & Analytics":
    sql_page.sql_queries_page()

# -------------------- CRUD PAGE --------------------
elif menu == "CRUD":
    crud_page.crud_page()

# -------------------- ABOUT PAGE --------------------
elif menu == "About":
    st.text("This Project is created by Poorvaj Naresh S P using Streamlit with Python and SQL")
