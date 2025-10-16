# crud_operations.py
"""
CRUD Operations Page
Full Create, Read, Update, Delete operations on player and match stats
using form-based UI. Useful for learners to understand database manipulation.
"""

import streamlit as st
import mysql.connector
import pandas as pd

# Database config
DB_CONFIG = {
    "host": "mysql-cricbuzz-dscricbuzzlivestats.b.aivencloud.com",
    "user": "avnadmin",
    "password": "AVNS_VgGogs_zOjn3OawLe9q",
    "database": "defaultdb"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_all():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM player_stats", conn)
    conn.close()
    return df

def insert_player(player_id, player_name, match_id, runs, balls, fours, sixes, wickets, overs, maidens, runs_conceded):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO player_stats
        (player_id, player_name, match_id, runs, balls, fours, sixes, wickets, overs, maidens, runs_conceded)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (player_id, player_name, match_id, runs, balls, fours, sixes, wickets, overs, maidens, runs_conceded))
    conn.commit()
    conn.close()

def update_player(player_id, match_id, runs, balls, wickets):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE player_stats
        SET runs=%s, balls=%s, wickets=%s
        WHERE player_id=%s AND match_id=%s
    """, (runs, balls, wickets, player_id, match_id))
    conn.commit()
    conn.close()

def delete_player(player_id, match_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM player_stats WHERE player_id=%s AND match_id=%s", (player_id, match_id))
    conn.commit()
    conn.close()

def app():
    st.title("📝 CRUD Operations Page")
    st.write("Full **Create, Read, Update, Delete** operations on player and match stats using form-based UI.")
    st.write("👉 Useful for learners to understand database manipulation.")

    st.subheader("📌 Create (Add New Player Stats)")
    with st.form("create_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            player_id = st.number_input("Player ID", min_value=1, step=1)
            player_name = st.text_input("Player Name")
            match_id = st.number_input("Match ID", min_value=1, step=1)
        with c2:
            runs = st.number_input("Runs", min_value=0, step=1)
            balls = st.number_input("Balls", min_value=0, step=1)
            fours = st.number_input("Fours", min_value=0, step=1)
        with c3:
            sixes = st.number_input("Sixes", min_value=0, step=1)
            wickets = st.number_input("Wickets", min_value=0, step=1)
            overs = st.number_input("Overs", min_value=0.0, step=0.1)
            maidens = st.number_input("Maidens", min_value=0, step=1)
            runs_conceded = st.number_input("Runs Conceded", min_value=0, step=1)

        submitted = st.form_submit_button("Add Record")
        if submitted:
            insert_player(player_id, player_name, match_id, runs, balls, fours, sixes, wickets, overs, maidens, runs_conceded)
            st.success(f"✅ Record for {player_name} (Match {match_id}) inserted!")

    st.subheader("📖 Read (View All Stats)")
    df = fetch_all()
    st.dataframe(df, use_container_width=True)

    st.subheader("✏️ Update Stats")
    with st.form("update_form"):
        u_player_id = st.number_input("Player ID (to update)", min_value=1, step=1)
        u_match_id = st.number_input("Match ID (to update)", min_value=1, step=1)
        u_runs = st.number_input("New Runs", min_value=0, step=1)
        u_balls = st.number_input("New Balls", min_value=0, step=1)
        u_wickets = st.number_input("New Wickets", min_value=0, step=1)
        update_btn = st.form_submit_button("Update Record")
        if update_btn:
            update_player(u_player_id, u_match_id, u_runs, u_balls, u_wickets)
            st.success(f"✅ Record for Player {u_player_id} (Match {u_match_id}) updated!")

    st.subheader("🗑️ Delete Stats")
    with st.form("delete_form"):
        d_player_id = st.number_input("Player ID (to delete)", min_value=1, step=1)
        d_match_id = st.number_input("Match ID (to delete)", min_value=1, step=1)
        delete_btn = st.form_submit_button("Delete Record")
        if delete_btn:
            delete_player(d_player_id, d_match_id)
            st.warning(f"⚠️ Record for Player {d_player_id} (Match {d_match_id}) deleted!")


app()
