import streamlit as st
import pandas as pd
import mysql.connector

DB_CONFIG = {
    "host": "mysql-cricbuzz-dscricbuzzlivestats.b.aivencloud.com",
    "user": "avnadmin",
    "password": "AVNS_VgGogs_zOjn3OawLe9q",
    "database": "defaultdb"
}

def run_query(query):
    """Run a SQL query and return results as DataFrame."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

def display_leaderboards():
    st.subheader("🏏 Top 10 Run Scorers")
    query1 = """
        SELECT player_name, SUM(runs) AS Runs, COUNT(match_id) AS Matches
        FROM player_stats
        GROUP BY player_id, player_name
        ORDER BY Runs DESC
        LIMIT 10;
    """
    df1 = run_query(query1)
    st.dataframe(df1, use_container_width=True)

    st.subheader("🎯 Top 10 Highest Scores")
    query2 = """
        SELECT player_name, MAX(runs) AS Highest_Score
        FROM player_stats
        GROUP BY player_id, player_name
        ORDER BY Highest_Score DESC
        LIMIT 10;
    """
    df2 = run_query(query2)
    st.dataframe(df2, use_container_width=True)

    st.subheader("🔥 Top 10 Wicket-Takers")
    query3 = """
        SELECT player_name, SUM(wickets) AS Wickets, COUNT(match_id) AS Matches
        FROM player_stats
        GROUP BY player_id, player_name
        ORDER BY Wickets DESC
        LIMIT 10;
    """
    df3 = run_query(query3)
    st.dataframe(df3, use_container_width=True)

def app():
    st.title("🏆 Top Player Stats (From MySQL)")
    st.write("Leaderboard tables computed from stored match data.")

    if st.button("Show Leaderboards"):
        display_leaderboards()



app()
