import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

def crud_page():
    # ------------------ DATABASE CONNECTION ------------------
    # 🔹 Replace password if needed → example: "mysql+pymysql://root:1234@localhost/cricket_db"
    engine = create_engine("mysql+pymysql://root:@localhost/cricket_db")
    
    
    # ------------------ FETCH DATA ------------------
    def load_players():
        query = "SELECT * FROM players"
        df = pd.read_sql(query, engine)
        return df
    
    # ------------------ ADD PLAYER ------------------
    def add_player(name, team, matches, runs, wickets):
        query = text("""
            INSERT INTO players (name, team, matches, runs, wickets)
            VALUES (:name, :team, :matches, :runs, :wickets)
        """)
        with engine.begin() as conn:
            conn.execute(query, {"name": name, "team": team, "matches": matches, "runs": runs, "wickets": wickets})
    
    # ------------------ UPDATE PLAYER ------------------
    def update_player(pid, name, team, matches, runs, wickets):
        query = text("""
            UPDATE players 
            SET name=:name, team=:team, matches=:matches, runs=:runs, wickets=:wickets
            WHERE id=:pid
        """)
        with engine.begin() as conn:
            conn.execute(query, {
                "pid": pid, "name": name, "team": team,
                "matches": matches, "runs": runs, "wickets": wickets
            })
    
    # ------------------ DELETE PLAYER ------------------
    def delete_player(pid):
        query = text("DELETE FROM players WHERE id=:pid")
        with engine.begin() as conn:
            conn.execute(query, {"pid": pid})
    
    
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
        st.dataframe(df, use_container_width=True)
    
    # ------------------ UPDATE PLAYER PAGE ------------------
    elif choice == "Update Player":
        st.subheader("✏️ Update Player Stats")
        df = load_players()
        
        if df.empty:
            st.warning("⚠ No players found in database.")
        else:
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
    
        if df.empty:
            st.warning("⚠ No players to delete.")
        else:
            player_list = df['id'].tolist()
            pid = st.selectbox("Select Player ID to Delete", player_list)
    
            if st.button("Delete"):
                delete_player(pid)
                st.error("❌ Player Deleted Successfully!")
    
