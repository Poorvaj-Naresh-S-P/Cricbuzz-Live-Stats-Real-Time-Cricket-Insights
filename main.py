import streamlit as st

st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide")
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Home","Live Matches","Top Player Stats","SQL Queries & Analytics","CRUD","About"])

if menu == "Home":
    st.title("🏏 Cricbuzz LiveStats Dashboard")
    st.markdown("""
    Welcome to **Cricbuzz LiveStats** — an interactive cricket analytics platform that brings together **live match updates**,  
    **player performance statistics**, **database-driven insights**, and **custom data management tools**, all in one place.

    ---
    ### 🎯 Project Objective
    This project is designed to:
    - Demonstrate integration of **Live Cricket APIs** using RapidAPI
    - Store & manage player data using **MySQL Database**
    - Perform **SQL Query Analysis** for learning and visualization
    - Support **CRUD Operations** to manage player statistics manually
    - Present analytics using **Streamlit Interactive UI**
    
    ---
    ### 🛠️ Tools & Technologies Used
    | Component | Technology |
    |----------|------------|
    | Frontend UI | Streamlit (Python Web UI) |
    | Backend / App Logic | Python |
    | Database | MySQL (XAMPP Server) |
    | External Data Source | Cricbuzz API (via RapidAPI) |
    | Data Visualization | Plotly / Streamlit Charts |
    
    ---
    ### 📌 Navigation Guide
    Use the **sidebar menu** to explore features:

    | Page | Description |
    |------|-------------|
    | **Live Matches** | View Live, Recent & Upcoming match details from API |
    | **Top Player Stats** | ICC Rankings: Batsmen & Bowlers across formats |
    | **SQL Queries & Analytics** | Run and visualize **25 SQL Practice Queries** |
    | **CRUD** | Add / Update / Delete Player Stats in MySQL |
    | **About** | Project credits & developer info |

    ---
    ### 📁 Project Folder Structure
    ```
    📦 Cricbuzz_LiveStats
    ├── main.py                       # Main navigation & dashboard routing
    ├── 1_live_matches.py             # Live / Recent / Upcoming match fetch page
    ├── 2_top_stats.py                # ICC Rankings & Stats visualizations
    ├── 3_sql_queries.py              # 25 SQL practice queries + analytics UI
    ├── 4_crud_operations.py          # Player CRUD operations (MySQL)
    ├── requirements.txt              # Python dependencies
    └── README.md                     # Project documentation
    ```

    ---
    ### 📄 Project Documentation
    If your documentation exists on GitHub or local, update link below.

    🔗 **Documentation Link:** *https://github.com/Poorvaj-Naresh-S-P/Cricbuzz-Live-Stats-Real-Time-Cricket-Insights*

    ---
    ### ✅ Ready to Begin?
    Use the **left sidebar** and start exploring the pages!
    """)

    st.success("Tip: Start with 'Live Matches' to see real-time game data.")


if menu == "Live Matches":
    st.title("🏏 Cricbuzz LiveStats — Live, Recent and Upcoming Matches")   
    pg_live = st.navigation([
        st.Page("1_live_matches.py", title="Live Matches Page", icon="🔥")
    ])
    pg_live.run()

if menu == "Top Player Stats":
    #st.title("🏏 Cricbuzz LiveStats — Top Player Stats")  
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
    
