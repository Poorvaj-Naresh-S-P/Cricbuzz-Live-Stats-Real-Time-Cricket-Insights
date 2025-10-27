import streamlit as st
import mysql.connector
import pandas as pd

# ------------------ DATABASE CONNECTION ------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="cricket"
    )

# ------------------ FETCH DATA ------------------
def load_players():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM players", conn)
    conn.close()
    return df

# ------------------ ADD PLAYER ------------------
def add_player(name, team, matches, runs, wickets):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO players (name, team, matches, runs, wickets) VALUES (%s,%s,%s,%s,%s)",
                   (name, team, matches, runs, wickets))
    conn.commit()
    conn.close()

# ------------------ UPDATE PLAYER ------------------
def update_player(pid, name, team, matches, runs, wickets):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE players SET name=%s, team=%s, matches=%s, runs=%s, wickets=%s WHERE id=%s
    """,(name, team, matches, runs, wickets, pid))
    conn.commit()
    conn.close()

# ------------------ DELETE PLAYER ------------------
def delete_player(pid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id=%s",(pid,))
    conn.commit()
    conn.close()

# =======================================================
# STREAMLIT UI
# =======================================================
st.title("🏏 Cricbuzz Player Stats - CRUD (Streamlit + MySQL)")

menu = ["Add Player", "View Players", "Update Player", "Delete Player"]
choice = st.sidebar.selectbox("Navigation", menu)

# ------------------ ADD PLAYER PAGE ------------------
if choice == "Add Player":
    st.subheader("➕ Add New Player")

    name = st.text_input("Player Name")
    team = st.text_input("Team Name")
    matches = st.number_input("Matches", min_value=0, step=1)
    runs = st.number_input("Runs", min_value=0, step=1)
    wickets = st.number_input("Wickets", min_value=0, step=1)

    if st.button("Add Player"):
        add_player(name, team, matches, runs, wickets)
        st.success(f"✅ Player '{name}' added successfully!")

# ------------------ VIEW PLAYERS PAGE ------------------
elif choice == "View Players":
    st.subheader("📋 Player Stats Table")
    df = load_players()
    st.dataframe(df)

# ------------------ UPDATE PLAYER PAGE ------------------
elif choice == "Update Player":
    st.subheader("✏️ Update Player Stats")
    df = load_players()
    player_list = df['id'].tolist()
    
    pid = st.selectbox("Select Player ID", player_list)
    player_data = df[df['id']==pid].iloc[0]

    name = st.text_input("Name", player_data.name)
    team = st.text_input("Team", player_data.team)
    matches = st.number_input("Matches", value=player_data.matches)
    runs = st.number_input("Runs", value=player_data.runs)
    wickets = st.number_input("Wickets", value=player_data.wickets)

    if st.button("Update"):
        update_player(pid, name, team, matches, runs, wickets)
        st.success("✅ Player updated successfully!")

# ------------------ DELETE PLAYER PAGE ------------------
elif choice == "Delete Player":
    st.subheader("🗑 Delete Player")
    df = load_players()
    player_list = df['id'].tolist()

    pid = st.selectbox("Select Player ID to Delete", player_list)

    if st.button("Delete"):
        delete_player(pid)
        st.error("❌ Player Deleted Successfully!")
