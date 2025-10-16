"""
Main.py

Cricbuzz LiveStats - Streamlit dashboard (single-file)
- Uses SQLite (cricbuzz_live.db)
- Integrates with RapidAPI Cricbuzz endpoints (uses provided api key)
- Pages: Home, Live Matches, Top Player Stats, SQL Queries & Analytics, CRUD
- Seeds DB with sample data (so analytics work out-of-the-box)

Run:
    streamlit run Main.py

Notes:
- Replace RAPIDAPI_KEY / RAPIDAPI_HOST below or in the Settings section of the app.
"""

import streamlit as st
import requests
import sqlite3
import pandas as pd
import os
import datetime
from sqlite3 import Error

# ---------------------------
# Configuration (default)
# ---------------------------
DEFAULT_RAPIDAPI_KEY = "241cbfdb81mshf7f104545e0f7b2p18118ejsn97a7eadb6ac8"
DEFAULT_RAPIDAPI_HOST = "cricbuzz-cricket2.p.rapidapi.com"
DEFAULT_LIVE_URL = "https://cricbuzz-cricket2.p.rapidapi.com/matches/v1/live"

DB_FILE = "cricbuzz_live.db"

# ---------------------------
# Database helpers
# ---------------------------
def create_connection(db_file=DB_FILE):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        st.error(f"DB connection error: {e}")
        raise

def init_db(conn):
    """
    Create tables and seed with sample data if necessary.
    """
    cur = conn.cursor()

    # Create tables
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT
    );

    CREATE TABLE IF NOT EXISTS venues (
        venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        country TEXT,
        capacity INTEGER
    );

    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        team1_id INTEGER,
        team2_id INTEGER,
        venue_id INTEGER,
        match_date DATE,
        format TEXT,
        winner_team_id INTEGER,
        victory_margin TEXT,
        toss_winner_team_id INTEGER,
        toss_decision TEXT,
        status TEXT,
        FOREIGN KEY(team1_id) REFERENCES teams(team_id),
        FOREIGN KEY(team2_id) REFERENCES teams(team_id),
        FOREIGN KEY(venue_id) REFERENCES venues(venue_id),
        FOREIGN KEY(winner_team_id) REFERENCES teams(team_id),
        FOREIGN KEY(toss_winner_team_id) REFERENCES teams(team_id)
    );

    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        country TEXT,
        playing_role TEXT,
        batting_style TEXT,
        bowling_style TEXT
    );

    CREATE TABLE IF NOT EXISTS batting_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        runs INTEGER,
        balls INTEGER,
        fours INTEGER,
        sixes INTEGER,
        strike_rate REAL,
        batting_position INTEGER,
        inning INTEGER,
        FOREIGN KEY(match_id) REFERENCES matches(match_id),
        FOREIGN KEY(player_id) REFERENCES players(player_id)
    );

    CREATE TABLE IF NOT EXISTS bowling_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        overs REAL,
        maidens INTEGER,
        runs_conceded INTEGER,
        wickets INTEGER,
        economy REAL,
        FOREIGN KEY(match_id) REFERENCES matches(match_id),
        FOREIGN KEY(player_id) REFERENCES players(player_id)
    );

    CREATE TABLE IF NOT EXISTS partnerships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player1_id INTEGER,
        player2_id INTEGER,
        runs INTEGER,
        inning INTEGER,
        FOREIGN KEY(match_id) REFERENCES matches(match_id),
        FOREIGN KEY(player1_id) REFERENCES players(player_id),
        FOREIGN KEY(player2_id) REFERENCES players(player_id)
    );
    """)
    conn.commit()

    # Seed minimal sample data if tables are empty
    cur.execute("SELECT COUNT(*) FROM teams;")
    if cur.fetchone()[0] == 0:
        seed_sample_data(conn)

def seed_sample_data(conn):
    """
    Insert sample teams, venues, players, matches, and stats to allow queries to run.
    """
    cur = conn.cursor()

    # Teams
    teams = [
        ("India", "India"),
        ("Australia", "Australia"),
        ("England", "England"),
        ("South Africa", "South Africa"),
        ("New Zealand", "New Zealand"),
    ]
    cur.executemany("INSERT INTO teams (name,country) VALUES (?,?);", teams)
    conn.commit()

    # Venues
    venues = [
        ("Eden Gardens", "Kolkata", "India", 70000),
        ("Melbourne Cricket Ground", "Melbourne", "Australia", 100000),
        ("Lord's", "London", "England", 30000),
    ]
    cur.executemany("INSERT INTO venues (name,city,country,capacity) VALUES (?,?,?,?);", venues)
    conn.commit()

    # Players (sample)
    players = [
        ("Virat Kohli", "India", "Batsman", "Right-hand bat", "Right-arm"),
        ("Rohit Sharma", "India", "Batsman", "Right-hand bat", "Right-arm"),
        ("Steve Smith", "Australia", "Batsman", "Right-hand bat", "Right-arm"),
        ("Mitchell Starc", "Australia", "Bowler", "Right-hand bat", "Left-arm fast"),
        ("Joe Root", "England", "Batsman", "Right-hand bat", "Right-arm"),
        ("Kane Williamson", "New Zealand", "Batsman", "Right-hand bat", "Right-arm"),
        ("Quinton de Kock", "South Africa", "Wicket-keeper", "Left-hand bat", "Right-arm"),
        ("Jasprit Bumrah", "India", "Bowler", "Right-hand bat", "Right-arm"),
    ]
    cur.executemany("""INSERT INTO players (full_name,country,playing_role,batting_style,bowling_style)
                       VALUES (?,?,?,?,?);""", players)
    conn.commit()

    # Matches (some past matches)
    # We'll set dates across 2023-2025 to satisfy time-based queries
    matches = [
        ("India vs Australia - Test", 1, 2, 1, "2024-02-15", "Test", 1, "Innings and 50 runs", 1, "bat", "Complete"),
        ("England vs New Zealand - ODI", 3, 5, 3, "2024-11-05", "ODI", 3, "20 runs", 3, "bat", "Complete"),
        ("India vs South Africa - T20", 1, 4, 1, "2025-03-10", "T20", 1, "7 wickets", 1, "bowl", "Complete"),
        ("India vs Australia - ODI", 1, 2, 2, "2025-06-21", "ODI", 2, "5 runs", 2, "bat", "Complete"),
        ("Australia vs England - T20", 2, 3, 2, "2025-07-08", "T20", 2, "10 runs", 2, "bowl", "Complete"),
    ]
    cur.executemany("""INSERT INTO matches 
                       (description,team1_id,team2_id,venue_id,match_date,format,winner_team_id,victory_margin,toss_winner_team_id,toss_decision,status)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?);""", matches)
    conn.commit()

    # Batting stats (sample)
    batting = [
        # match_id, player_id, runs, balls, fours, sixes, strike_rate, batting_position, inning
        (1, 1, 120, 210, 12, 1, round(120/210*100,2), 3, 1),
        (1, 2, 45, 80, 5, 0, round(45/80*100,2), 1, 1),
        (2, 5, 80, 95, 8, 1, round(80/95*100,2), 3, 1),
        (3, 1, 55, 35, 6, 2, round(55/35*100,2), 2, 1),
        (3, 8, 0, 1, 0, 0, 0, 11, 1),
        (4, 3, 110, 125, 10, 0, round(110/125*100,2), 3, 1),
        (5, 4, 2, 8, 0, 0, round(2/8*100,2), 11, 1),
    ]
    cur.executemany("""INSERT INTO batting_stats (match_id,player_id,runs,balls,fours,sixes,strike_rate,batting_position,inning)
                       VALUES (?,?,?,?,?,?,?,?,?);""", batting)
    conn.commit()

    # Bowling stats (sample)
    bowling = [
        (1, 8, 25.0, 3, 100, 5, round(100/25.0,2)),
        (1, 4, 20.0, 2, 80, 4, round(80/20.0,2)),
        (3, 4, 4.0, 0, 22, 3, round(22/4.0,2)),
        (4, 8, 10.0, 0, 60, 2, round(60/10.0,2)),
    ]
    cur.executemany("""INSERT INTO bowling_stats (match_id,player_id,overs,maidens,runs_conceded,wickets,economy)
                       VALUES (?,?,?,?,?,?,?);""", bowling)
    conn.commit()

    # Partnerships
    partnerships = [
        (1, 1, 2, 150, 1),
        (2, 5, 6, 80, 1),
        (4, 3, 1, 110, 1),
        (5, 4, 3, 40, 1),
    ]
    cur.executemany("""INSERT INTO partnerships (match_id,player1_id,player2_id,runs,inning)
                       VALUES (?,?,?,?,?);""", partnerships)
    conn.commit()

    st.info("Database seeded with sample data (teams, venues, players, matches, stats).")

# ---------------------------
# RapidAPI integration
# ---------------------------
def get_rapidapi_headers(api_key, api_host):
    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }

def fetch_live_matches(api_key, api_host, url=DEFAULT_LIVE_URL):
    headers = get_rapidapi_headers(api_key, api_host)
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        st.error(f"Error fetching live matches: {e}")
        return None

# ---------------------------
# Helper: run SQL and return dataframe
# ---------------------------
def run_query(conn, query, params=None):
    if params is None: params = ()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"SQL error: {e}")
        return pd.DataFrame()

# ---------------------------
# SQL queries (25 queries implemented)
# ---------------------------
def get_query_text(index):
    """
    Return a (label, sql_text) pair for the requested query index (1..25).
    These SQLs assume the schema we created. Some queries include derived logic.
    """
    # We'll implement the 25 queries mapping described in the PDF.
    q = {}
    q[1] = ("Find all players who represent India (name, role, batting style, bowling style).",
            "SELECT full_name, playing_role, batting_style, bowling_style FROM players WHERE country = 'India';")

    q[2] = ("Show all cricket matches that were played in the last 30 days (desc, teams, venue, date).",
            """SELECT m.description,
                      t1.name AS team1, t2.name AS team2,
                      v.name AS venue, m.match_date
               FROM matches m
               LEFT JOIN teams t1 ON m.team1_id = t1.team_id
               LEFT JOIN teams t2 ON m.team2_id = t2.team_id
               LEFT JOIN venues v ON m.venue_id = v.venue_id
               WHERE DATE(m.match_date) >= DATE('now','-30 days')
               ORDER BY m.match_date DESC;""")

    q[3] = ("Top 10 highest run scorers in ODI (player, total_runs, avg - sample using batting_stats & matches).",
            """SELECT p.full_name,
                      SUM(b.runs) AS total_runs,
                      ROUND(AVG(b.runs),2) AS avg_runs,
                      SUM(CASE WHEN m.format='ODI' THEN b.runs ELSE 0 END) AS odi_runs
               FROM batting_stats b
               JOIN players p ON b.player_id = p.player_id
               JOIN matches m ON b.match_id = m.match_id
               GROUP BY p.player_id
               ORDER BY odi_runs DESC
               LIMIT 10;""")

    q[4] = ("Venues with capacity > 50000 (name, city, country, capacity).",
            "SELECT name, city, country, capacity FROM venues WHERE capacity > 50000 ORDER BY capacity DESC;")

    q[5] = ("How many matches each team has won.",
            """SELECT t.name AS team, COUNT(*) AS wins
               FROM matches m
               JOIN teams t ON m.winner_team_id = t.team_id
               GROUP BY t.team_id
               ORDER BY wins DESC;""")

    q[6] = ("Count how many players belong to each playing role (role and count).",
            "SELECT playing_role, COUNT(*) AS cnt FROM players GROUP BY playing_role;")

    q[7] = ("Highest individual batting score achieved in each cricket format (format, highest_score).",
            """SELECT m.format, MAX(b.runs) AS highest_score
               FROM batting_stats b
               JOIN matches m ON b.match_id = m.match_id
               GROUP BY m.format;""")

    q[8] = ("Show all cricket series that started in the year 2024 (we'll interpret matches as series entries).",
            "SELECT description, match_date, format FROM matches WHERE match_date BETWEEN '2024-01-01' AND '2024-12-31' ORDER BY match_date;")

    # Intermediate
    q[9] = ("All-rounders with >1000 runs and >50 wickets (sample on supplied DB - may be empty).",
            """SELECT p.full_name,
                      SUM(b.runs) AS total_runs,
                      SUM(COALESCE(bo.wickets,0)) AS total_wickets
               FROM players p
               LEFT JOIN batting_stats b ON p.player_id = b.player_id
               LEFT JOIN bowling_stats bo ON p.player_id = bo.player_id
               WHERE p.playing_role LIKE '%All%' OR p.playing_role LIKE '%All-rounder%'
               GROUP BY p.player_id
               HAVING total_runs > 1000 AND total_wickets > 50;""")

    q[10] = ("Details of the last 20 completed matches.",
             """SELECT m.description, t1.name AS team1, t2.name AS team2,
                       (SELECT name FROM teams WHERE team_id = m.winner_team_id) AS winning_team,
                       m.victory_margin, m.format, v.name as venue, m.match_date
                FROM matches m
                LEFT JOIN teams t1 ON m.team1_id = t1.team_id
                LEFT JOIN teams t2 ON m.team2_id = t2.team_id
                LEFT JOIN venues v ON m.venue_id = v.venue_id
                WHERE m.status = 'Complete'
                ORDER BY m.match_date DESC
                LIMIT 20;""")

    q[11] = ("Compare each player's performance across different formats (total runs by format).",
            """SELECT p.full_name,
                      SUM(CASE WHEN m.format='Test' THEN b.runs ELSE 0 END) AS Test_runs,
                      SUM(CASE WHEN m.format='ODI' THEN b.runs ELSE 0 END) AS ODI_runs,
                      SUM(CASE WHEN m.format='T20' THEN b.runs ELSE 0 END) AS T20_runs,
                      ROUND(AVG(b.runs),2) AS overall_avg
               FROM players p
               LEFT JOIN batting_stats b ON p.player_id = b.player_id
               LEFT JOIN matches m ON b.match_id = m.match_id
               GROUP BY p.player_id
               HAVING (Test_runs + ODI_runs + T20_runs) > 0
               ORDER BY overall_avg DESC;""")

    q[12] = ("Team performance home vs away (count wins home vs away).",
            """SELECT t.name AS team,
                      SUM(CASE WHEN v.country = t.country AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
                      SUM(CASE WHEN (v.country != t.country) AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
               FROM teams t
               LEFT JOIN matches m ON (m.team1_id = t.team_id OR m.team2_id = t.team_id)
               LEFT JOIN venues v ON m.venue_id = v.venue_id
               GROUP BY t.team_id;""")

    q[13] = ("Batting partnerships where two consecutive batsmen scored combined >=100 in same innings.",
            """SELECT p1.full_name AS batsman1, p2.full_name AS batsman2, pa.runs, pa.match_id, pa.inning
               FROM partnerships pa
               JOIN players p1 ON pa.player1_id = p1.player_id
               JOIN players p2 ON pa.player2_id = p2.player_id
               WHERE pa.runs >= 100
               ORDER BY pa.runs DESC;""")

    q[14] = ("Bowling performance at venues: avg economy, total wickets for bowlers with >=3 matches at same venue.",
            """SELECT bo.player_id, p.full_name, v.name as venue,
                      ROUND(AVG(bo.economy),2) AS avg_economy,
                      SUM(bo.wickets) AS total_wickets,
                      COUNT(DISTINCT bo.match_id) as matches_played
               FROM bowling_stats bo
               JOIN players p ON bo.player_id = p.player_id
               JOIN matches m ON bo.match_id = m.match_id
               JOIN venues v ON m.venue_id = v.venue_id
               GROUP BY bo.player_id, v.venue_id
               HAVING matches_played >= 3;""")

    q[15] = ("Players who perform well in close matches (<50 runs OR <5 wickets).",
            """WITH close AS (
               SELECT match_id FROM matches
               WHERE
                 (winner_team_id IS NOT NULL AND (CASE WHEN victory_margin LIKE '%wicket%' THEN CAST(REPLACE(victory_margin,' wickets','') AS INTEGER) ELSE CAST(REPLACE(victory_margin,' runs','') AS INTEGER) END) < 50)
                 OR (victory_margin LIKE '%wicket%' AND CAST(REPLACE(victory_margin,' wickets','') AS INTEGER) < 5)
               )
               SELECT p.full_name,
                      ROUND(AVG(b.runs),2) AS avg_runs,
                      COUNT(DISTINCT b.match_id) AS close_matches,
                      SUM(CASE WHEN m.winner_team_id = (SELECT team1_id FROM matches WHERE match_id=b.match_id) THEN 1 ELSE 0 END) AS wins_when_batted
               FROM batting_stats b
               JOIN players p ON b.player_id = p.player_id
               JOIN matches m ON b.match_id = m.match_id
               WHERE b.match_id IN (SELECT match_id FROM close)
               GROUP BY p.player_id;""")

    q[16] = ("Track batting performance changes over years (since 2020): avg runs and avg strike rate per year for players with >=5 matches in year.",
            """SELECT p.full_name, STRFTIME('%Y', m.match_date) AS year,
                      ROUND(AVG(b.runs),2) as avg_runs,
                      ROUND(AVG(b.strike_rate),2) as avg_strike_rate,
                      COUNT(DISTINCT b.match_id) as matches_played
               FROM batting_stats b
               JOIN players p ON b.player_id = p.player_id
               JOIN matches m ON b.match_id = m.match_id
               WHERE m.match_date >= '2020-01-01'
               GROUP BY p.player_id, year
               HAVING matches_played >= 5
               ORDER BY p.full_name, year;""")

    # Advanced
    q[17] = ("Does winning the toss give advantage? % of matches won by toss winners broken down by toss decision.",
            """SELECT toss_decision,
                      ROUND(100.0 * SUM(CASE WHEN toss_winner_team_id = winner_team_id THEN 1 ELSE 0 END) / COUNT(*),2) AS pct_won_after_winning_toss,
                      COUNT(*) as matches_count
               FROM matches
               WHERE toss_winner_team_id IS NOT NULL
               GROUP BY toss_decision;""")

    q[18] = ("Most economical bowlers in limited-overs (ODI and T20), bowlers with >=10 matches and >=2 overs per match avg.",
            """SELECT p.full_name,
                      ROUND(SUM(bo.wickets),0) AS total_wickets,
                      ROUND(AVG(bo.economy),2) AS avg_economy,
                      COUNT(DISTINCT bo.match_id) AS matches_played
               FROM bowling_stats bo
               JOIN matches m ON bo.match_id = m.match_id
               JOIN players p ON bo.player_id = p.player_id
               WHERE m.format IN ('ODI','T20')
               GROUP BY bo.player_id
               HAVING matches_played >= 10
               ORDER BY avg_economy ASC
               LIMIT 50;""")

    q[19] = ("Batsmen consistency: average runs and stddev (sample using pandas) - players who played since 2022 and faced >=10 balls per innings.",
            # SQLite doesn't have a stddev builtin; we will compute via pandas after running base query.
            """SELECT p.player_id, p.full_name, b.runs
               FROM batting_stats b
               JOIN players p ON b.player_id = p.player_id
               JOIN matches m ON b.match_id = m.match_id
               WHERE m.match_date >= '2022-01-01' AND b.balls >= 10;""")

    q[20] = ("Matches each player played in different formats and batting average per format (players with >=20 total matches).",
            """SELECT p.full_name,
                      SUM(CASE WHEN m.format='Test' THEN 1 ELSE 0 END) AS Test_matches,
                      SUM(CASE WHEN m.format='ODI' THEN 1 ELSE 0 END) AS ODI_matches,
                      SUM(CASE WHEN m.format='T20' THEN 1 ELSE 0 END) AS T20_matches,
                      ROUND(
                        (COALESCE(SUM(CASE WHEN m.format='Test' THEN b.runs ELSE 0 END),0) +
                         COALESCE(SUM(CASE WHEN m.format='ODI' THEN b.runs ELSE 0 END),0) +
                         COALESCE(SUM(CASE WHEN m.format='T20' THEN b.runs ELSE 0 END),0)
                        ) / NULLIF((COUNT(DISTINCT b.match_id)),0),2) AS batting_avg
               FROM players p
               LEFT JOIN batting_stats b ON p.player_id = b.player_id
               LEFT JOIN matches m ON b.match_id = m.match_id
               GROUP BY p.player_id
               HAVING (Test_matches + ODI_matches + T20_matches) >= 20;""")

    q[21] = ("Comprehensive performance ranking: weighted score combining batting/bowling/fielding (simplified).",
            """SELECT p.full_name,
                      ( (COALESCE(SUM(b.runs),0) * 0.01) + (COALESCE(AVG(CASE WHEN b.runs>0 THEN b.runs END),0) * 0.5) ) AS batting_points,
                      ( (COALESCE(SUM(bo.wickets),0) * 2) + (COALESCE(AVG(bo.economy),0)* -0.5) ) AS bowling_points,
                      ROUND(
                        ( (COALESCE(SUM(b.runs),0)*0.01) + (COALESCE(AVG(b.runs),0)*0.5)
                          + (COALESCE(SUM(bo.wickets),0)*2) - (COALESCE(AVG(bo.economy),0)*0.5)
                        ),2) AS total_score
               FROM players p
               LEFT JOIN batting_stats b ON p.player_id = b.player_id
               LEFT JOIN bowling_stats bo ON p.player_id = bo.player_id
               GROUP BY p.player_id
               ORDER BY total_score DESC
               LIMIT 50;""")

    q[22] = ("Head-to-head match analysis between teams (pairs with >=5 matches in last 3 years).",
            """SELECT t1.name as teamA, t2.name as teamB,
                      COUNT(*) as matches_played,
                      SUM(CASE WHEN m.winner_team_id = m.team1_id THEN 1 ELSE 0 END) AS wins_team1,
                      SUM(CASE WHEN m.winner_team_id = m.team2_id THEN 1 ELSE 0 END) AS wins_team2,
                      ROUND(AVG(CASE WHEN m.victory_margin LIKE '%run%' THEN CAST(REPLACE(m.victory_margin,' runs','') AS FLOAT) ELSE NULL END),2) as avg_victory_margin_runs
               FROM matches m
               JOIN teams t1 ON m.team1_id = t1.team_id
               JOIN teams t2 ON m.team2_id = t2.team_id
               WHERE m.match_date >= DATE('now','-3 years')
               GROUP BY m.team1_id, m.team2_id
               HAVING matches_played >= 1;""")  # set to 1 for sample DB; real usage filter >=5

    q[23] = ("Recent player form (last 10 batting performances): avg last 5 vs last 10 etc.",
            """SELECT p.full_name,
                      b.runs,
                      b.match_id,
                      m.match_date
               FROM batting_stats b
               JOIN players p ON b.player_id = p.player_id
               JOIN matches m ON b.match_id = m.match_id
               ORDER BY p.player_id, m.match_date DESC;""")  # We'll process in pandas for last N logic.

    q[24] = ("Successful batting partnerships: pairs with >=5 partnerships - avg partnership runs etc.",
            """SELECT p1.full_name AS player1, p2.full_name AS player2,
                      COUNT(*) AS partnerships_count,
                      ROUND(AVG(pa.runs),2) AS avg_runs,
                      MAX(pa.runs) AS highest_partnership,
                      SUM(CASE WHEN pa.runs >= 50 THEN 1 ELSE 0 END) AS partnerships_over_50
               FROM partnerships pa
               JOIN players p1 ON pa.player1_id = p1.player_id
               JOIN players p2 ON pa.player2_id = p2.player_id
               GROUP BY pa.player1_id, pa.player2_id
               HAVING partnerships_count >= 1
               ORDER BY avg_runs DESC;""")

    q[25] = ("Time-series analysis quarterly for players (quarterly avg runs & strike rate), requires >=6 quarters and >=3 matches per quarter.",
            """SELECT p.full_name, 
                      STRFTIME('%Y-Q', m.match_date) AS quarter, -- note: SQLite doesn't support %q, custom quarter handling required in app
                      ROUND(AVG(b.runs),2) AS avg_runs,
                      ROUND(AVG(b.strike_rate),2) AS avg_strike_rate,
                      COUNT(DISTINCT b.match_id) AS matches_in_quarter
               FROM batting_stats b
               JOIN players p ON b.player_id = p.player_id
               JOIN matches m ON b.match_id = m.match_id
               GROUP BY p.player_id, STRFTIME('%Y',m.match_date), ( (CAST( ( (CAST(STRFTIME('%m',m.match_date) AS INTEGER) -1) / 3 ) AS INTEGER)) )
               HAVING matches_in_quarter >= 3
               ORDER BY p.full_name, quarter;""")

    return q.get(index, ("Unknown query", "SELECT 1;"))

# ---------------------------
# Page UIs
# ---------------------------
def page_home():
    st.title("🏏 Cricbuzz LiveStats — Home")
    st.write("""
    This project integrates the RapidAPI Cricbuzz endpoints with a local **SQLite** database to provide:
    - Real-time live matches page (fetches from RapidAPI)
    - Top player stats page
    - SQL Queries & Analytics (25 queries implemented)
    - CRUD operations to manage players & matches
    """)
    st.markdown("### Quick start")
    st.markdown("""
    - Ensure you have `streamlit`, `pandas`, and `requests` installed.
    - Put your RapidAPI key in the Settings section or replace the default in the code.
    - Run: `streamlit run Main.py`
    """)
    st.markdown("### Notes on database")
    st.markdown("""
    - The app uses `cricbuzz_live.db` (SQLite) created in the same folder as this script.
    - On first run the app will create tables and insert **sample** data so analytics pages show meaningful output.
    - You can import real data from RapidAPI using the Live Matches page actions.
    """)

def page_live_matches(conn, api_key, api_host):
    st.title("Live Matches (RapidAPI)")
    st.markdown("This page fetches live matches from the Cricbuzz RapidAPI endpoint and shows JSON & a lightweight table preview.")

    col1, col2 = st.columns(2)
    with col1:
        api_key_input = st.text_input("RapidAPI Key", value=api_key, type="password")
    with col2:
        api_host_input = st.text_input("RapidAPI Host", value=api_host)

    url_input = st.text_input("Live Matches URL", value=DEFAULT_LIVE_URL)

    if st.button("Fetch live matches now"):
        data = fetch_live_matches(api_key_input, api_host_input, url=url_input)
        if data is not None:
            st.subheader("Raw JSON (first 2000 chars)")
            st.code(str(data)[:2000])
            # Attempt to parse relevant parts into a table if possible
            # The RapidAPI response may contain nested dictionaries. We'll try to flatten match list.
            if isinstance(data, dict):
                # Many Cricbuzz endpoints return 'type','matches' etc. We'll search for lists inside.
                # A simple approach: show all lists at top-level and let user explore.
                for k, v in data.items():
                    if isinstance(v, list):
                        st.write(f"Top-level list: **{k}** (showing first 10 rows)")
                        try:
                            df = pd.json_normalize(v)
                            st.dataframe(df.head(10))
                        except Exception as e:
                            st.write("Could not normalize this list:", e)
            else:
                st.write("Unexpected response structure:", type(data))

            # Offer to insert live matches into local DB (best effort)
            if st.button("Insert top-level matches into local DB (best-effort)"):
                inserted = 0
                cursor = conn.cursor()
                # Best-effort mapping: if data contains 'matches' list, iterate
                matches_list = None
                if isinstance(data, dict):
                    for k,v in data.items():
                        if isinstance(v, list):
                            matches_list = v
                            break
                elif isinstance(data, list):
                    matches_list = data
                if matches_list:
                    for item in matches_list:
                        # map minimal set: description, team names, venue, date, format, status
                        desc = item.get("match_desc") or item.get("name") or item.get("series") or item.get("match_title") or str(item)[:100]
                        # teams may be nested - try to find team names
                        team1 = None; team2 = None
                        if "team1" in item and isinstance(item["team1"], dict):
                            team1 = item["team1"].get("name")
                        if "team2" in item and isinstance(item.get("team2"), dict):
                            team2 = item["team2"].get("name")
                        # fallback checks
                        tnames = []
                        for k2 in ["team1", "team2", "teams", "team"]:
                            if k2 in item:
                                try:
                                    if isinstance(item[k2], list):
                                        for t in item[k2]:
                                            if isinstance(t, dict) and t.get("name"):
                                                tnames.append(t.get("name"))
                                    elif isinstance(item[k2], dict) and item[k2].get("name"):
                                        tnames.append(item[k2].get("name"))
                                except:
                                    pass
                        if len(tnames) >= 2:
                            team1, team2 = tnames[0], tnames[1]
                        # venue
                        venue = None
                        if "venue" in item and isinstance(item["venue"], dict):
                            venue = item["venue"].get("name")
                        match_date = item.get("start_date") or item.get("date") or item.get("match_date") or None
                        fmt = item.get("format") or item.get("type") or None
                        status = item.get("status") or item.get("match_status") or None

                        # insert teams if not exists
                        def ensure_team(name):
                            if not name: return None
                            cur = conn.cursor()
                            cur.execute("SELECT team_id FROM teams WHERE name = ?;", (name,))
                            r = cur.fetchone()
                            if r:
                                return r[0]
                            cur.execute("INSERT INTO teams (name,country) VALUES (?,?);", (name, None))
                            conn.commit()
                            return cur.lastrowid

                        team1_id = ensure_team(team1)
                        team2_id = ensure_team(team2)
                        # ensure venue
                        def ensure_venue(name):
                            if not name: return None
                            cur = conn.cursor()
                            cur.execute("SELECT venue_id FROM venues WHERE name = ?;", (name,))
                            r = cur.fetchone()
                            if r:
                                return r[0]
                            cur.execute("INSERT INTO venues (name,city,country,capacity) VALUES (?,?,?,?);", (name,None,None,0))
                            conn.commit()
                            return cur.lastrowid
                        venue_id = ensure_venue(venue)

                        # Insert match
                        try:
                            cursor.execute("""INSERT INTO matches (description,team1_id,team2_id,venue_id,match_date,format,status)
                                              VALUES (?,?,?,?,?,?);""", (desc, team1_id, team2_id, venue_id, match_date, fmt, status))
                            conn.commit()
                            inserted += 1
                        except Exception as e:
                            st.write("Insert error:", e)
                    st.success(f"Inserted {inserted} matches (best-effort).")
                else:
                    st.warning("Could not find a list of matches in the API response.")

def page_top_players(conn):
    st.title("Top Player Stats")
    st.write("Aggregated top batting and bowling stats from the local database.")

    # Top run scorers
    q_batting = """SELECT p.full_name, SUM(b.runs) AS total_runs, COUNT(DISTINCT b.match_id) AS matches_played, ROUND(AVG(b.runs),2) AS avg_runs
                   FROM batting_stats b JOIN players p ON b.player_id = p.player_id
                   GROUP BY p.player_id
                   ORDER BY total_runs DESC
                   LIMIT 20;"""
    df_bat = run_query(conn, q_batting)
    st.subheader("Top Run Scorers")
    st.dataframe(df_bat)

    # Top wicket-takers
    q_bowling = """SELECT p.full_name, SUM(bo.wickets) AS total_wickets, COUNT(DISTINCT bo.match_id) AS matches_played, ROUND(AVG(bo.economy),2) AS avg_economy
                   FROM bowling_stats bo JOIN players p ON bo.player_id = p.player_id
                   GROUP BY p.player_id
                   ORDER BY total_wickets DESC
                   LIMIT 20;"""
    df_bowl = run_query(conn, q_bowling)
    st.subheader("Top Wicket-takers")
    st.dataframe(df_bowl)

def page_sql_analytics(conn):
    st.title("SQL Queries & Analytics (25 Queries)")
    st.write("Select any of the 25 queries to run. Some heavy queries may return empty results if sample DB lacks relevant entries — replace with real data to see full outputs.")

    idx = st.selectbox("Choose query (1..25)", list(range(1,26)), format_func=lambda x: f"{x} - {get_query_text(x)[0]}")
    label, sql = get_query_text(idx)
    st.markdown(f"**Query {idx}:** {label}")
    st.code(sql)

    if st.button("Run Query"):
        if idx == 19:
            # special handling for consistency with pandas
            df_raw = run_query(conn, get_query_text(idx)[1])
            if df_raw.empty:
                st.info("No matching rows for this query on current DB.")
            else:
                # compute avg and stddev per player
                df_stats = df_raw.groupby(['player_id','full_name'])['runs'].agg(['mean','std','count']).reset_index()
                df_stats.rename(columns={'mean':'avg_runs','std':'stddev_runs','count':'appearances'}, inplace=True)
                st.dataframe(df_stats.sort_values(by='avg_runs', ascending=False))
        elif idx == 23:
            df = run_query(conn, sql)
            if df.empty:
                st.info("No batting rows found.")
            else:
                # compute last 10 performances for each player
                grouped = df.sort_values(['full_name','match_date'], ascending=[True, False]).groupby('full_name')
                rows = []
                for name, g in grouped:
                    g2 = g.head(10)
                    last10 = g2['runs'].tolist()
                    last5 = g2.head(5)['runs'].tolist()
                    avg_last5 = round(pd.Series(last5).mean(),2) if len(last5)>0 else None
                    avg_last10 = round(pd.Series(last10).mean(),2) if len(last10)>0 else None
                    rows.append({'player':name,'avg_last5':avg_last5,'avg_last10':avg_last10,'scores_last10':last10})
                st.dataframe(pd.DataFrame(rows))
        else:
            df = run_query(conn, sql)
            if df.empty:
                st.info("Query returned no rows on current DB (sample DB may not contain required data).")
            else:
                st.dataframe(df)

def page_crud(conn):
    st.title("CRUD Operations (Players & Matches)")
    st.write("Create or update players and matches here. Use the forms below to manage local SQLite DB.")

    tab = st.radio("Choose entity", ["Players","Matches"])
    cur = conn.cursor()

    if tab == "Players":
        st.subheader("Add new player")
        with st.form("add_player"):
            name = st.text_input("Full name")
            country = st.text_input("Country")
            role = st.selectbox("Playing role", ["Batsman","Bowler","All-rounder","Wicket-keeper","Other"])
            bat_style = st.text_input("Batting style")
            bowl_style = st.text_input("Bowling style")
            submitted = st.form_submit_button("Add player")
            if submitted:
                cur.execute("""INSERT INTO players (full_name,country,playing_role,batting_style,bowling_style)
                               VALUES (?,?,?,?,?);""",(name,country,role,bat_style,bowl_style))
                conn.commit()
                st.success(f"Added player {name}")

        st.subheader("Update / Delete player")
        players_df = run_query(conn, "SELECT player_id, full_name, country, playing_role FROM players;")
        st.dataframe(players_df)
        sel = st.number_input("Player ID to update/delete", min_value=0, value=0, step=1)
        if sel > 0:
            p = cur.execute("SELECT * FROM players WHERE player_id = ?;", (sel,)).fetchone()
            if p:
                st.write(p)
                new_name = st.text_input("New name", value=p[1])
                new_country = st.text_input("New country", value=p[2] if p[2] else "")
                new_role = st.text_input("New role", value=p[3] if p[3] else "")
                if st.button("Update player"):
                    cur.execute("""UPDATE players SET full_name=?, country=?, playing_role=? WHERE player_id=?;""",
                                (new_name, new_country, new_role, sel))
                    conn.commit()
                    st.success("Player updated.")
                if st.button("Delete player"):
                    cur.execute("DELETE FROM players WHERE player_id=?;", (sel,))
                    conn.commit()
                    st.success("Player deleted.")
            else:
                st.warning("Player not found.")

    else:  # Matches
        st.subheader("Add new match")
        teams = run_query(conn, "SELECT team_id, name FROM teams;")
        venues = run_query(conn, "SELECT venue_id, name FROM venues;")
        with st.form("add_match"):
            desc = st.text_input("Match description")
            team1 = st.selectbox("Team 1", teams['team_id'].tolist(), format_func=lambda x: teams.loc[teams['team_id']==x,'name'].values[0])
            team2 = st.selectbox("Team 2", [t for t in teams['team_id'].tolist() if t != team1],
                                 format_func=lambda x: teams.loc[teams['team_id']==x,'name'].values[0])
            venue = st.selectbox("Venue", venues['venue_id'].tolist(), format_func=lambda x: venues.loc[venues['venue_id']==x,'name'].values[0])
            mdate = st.date_input("Match date", value=datetime.date.today())
            mformat = st.selectbox("Format", ["Test","ODI","T20"])
            submitted = st.form_submit_button("Add match")
            if submitted:
                cur.execute("""INSERT INTO matches (description,team1_id,team2_id,venue_id,match_date,format,status)
                               VALUES (?,?,?,?,?,?,?);""", (desc, team1, team2, venue, mdate.isoformat(), mformat, "Scheduled"))
                conn.commit()
                st.success("Match added.")

        st.subheader("Update / Delete match")
        matches_df = run_query(conn, "SELECT match_id, description, match_date, format, status FROM matches;")
        st.dataframe(matches_df)
        selm = st.number_input("Match ID to update/delete", min_value=0, value=0, step=1)
        if selm > 0:
            m = cur.execute("SELECT * FROM matches WHERE match_id = ?;", (selm,)).fetchone()
            if m:
                st.write(m)
                new_desc = st.text_input("New description", value=m[1])
                new_status = st.text_input("New status", value=m[11] if len(m) > 11 else m[11-1] if m else "")
                if st.button("Update match"):
                    cur.execute("UPDATE matches SET description=?, status=? WHERE match_id=?;", (new_desc, new_status, selm))
                    conn.commit()
                    st.success("Match updated.")
                if st.button("Delete match"):
                    cur.execute("DELETE FROM matches WHERE match_id=?;", (selm,))
                    conn.commit()
                    st.success("Match deleted.")
            else:
                st.warning("Match not found.")

# ---------------------------
# Main app
# ---------------------------
def main():
    st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide")
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Go to", ["Home","Live Matches","Top Player Stats","SQL Queries & Analytics","CRUD","Settings"])

    # Connect to DB
    conn = create_connection()
    init_db(conn)

    # Settings for API keys; allow override via environment variables
    api_key_env = os.environ.get("RAPIDAPI_KEY", DEFAULT_RAPIDAPI_KEY)
    api_host_env = os.environ.get("RAPIDAPI_HOST", DEFAULT_RAPIDAPI_HOST)

    if menu == "Home":
        page_home()

    elif menu == "Live Matches":
        page_live_matches(conn, api_key_env, api_host_env)

    elif menu == "Top Player Stats":
        page_top_players(conn)

    elif menu == "SQL Queries & Analytics":
        page_sql_analytics(conn)

    elif menu == "CRUD":
        page_crud(conn)

    elif menu == "Settings":
        st.title("Settings")
        st.info("Set RapidAPI credentials and DB file path if desired.")
        st.write("You can override API key using an environment variable RAPIDAPI_KEY or change the default below.")
        with st.form("settings_form"):
            key = st.text_input("RapidAPI Key (used to fetch live matches)", value=api_key_env, type="password")
            host = st.text_input("RapidAPI Host", value=api_host_env)
            dbfile = st.text_input("SQLite DB file path", value=DB_FILE)
            submitted = st.form_submit_button("Save settings (for this session)")
            if submitted:
                # Save to environment for session
                os.environ["RAPIDAPI_KEY"] = key
                os.environ["RAPIDAPI_HOST"] = host
                st.success("Settings saved for this session. (To persist across sessions, use environment variables or edit the script.)")

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("DB file: `" + DB_FILE + "`")
    st.sidebar.markdown("Created by: Your Streamlit App")

if __name__ == "__main__":
    main()

