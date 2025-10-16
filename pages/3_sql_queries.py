# sql_queries_analytics.py
"""
SQL Queries & Analytics Page
Integrates 25+ SQL queries on the cricket database.
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

def run_query(query):
    """Run SQL query and return DataFrame"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# ✅ All 25 SQL Queries
QUERIES = {
    # Beginner (Q1–Q8)
    "Q1: Players who represent India": """
        SELECT full_name, playing_role, batting_style, bowling_style
        FROM players
        WHERE country = 'India';
    """,
    "Q2: Matches in last 30 days": """
        SELECT match_desc, team1, team2, venue_name, city, match_date
        FROM matches
        WHERE match_date >= CURDATE() - INTERVAL 30 DAY
        ORDER BY match_date DESC;
    """,
    "Q3: Top 10 ODI run scorers": """
        SELECT player_name, total_runs, batting_avg, centuries
        FROM player_career_stats
        WHERE format = 'ODI'
        ORDER BY total_runs DESC
        LIMIT 10;
    """,
    "Q4: Venues with > 50,000 capacity": """
        SELECT venue_name, city, country, capacity
        FROM venues
        WHERE capacity > 50000
        ORDER BY capacity DESC;
    """,
    "Q5: Matches each team has won": """
        SELECT winner AS team_name, COUNT(*) AS total_wins
        FROM matches
        WHERE winner IS NOT NULL
        GROUP BY winner
        ORDER BY total_wins DESC;
    """,
    "Q6: Count players by role": """
        SELECT playing_role, COUNT(*) AS player_count
        FROM players
        GROUP BY playing_role;
    """,
    "Q7: Highest score per format": """
        SELECT format, MAX(high_score) AS highest_score
        FROM player_career_stats
        GROUP BY format;
    """,
    "Q8: Series started in 2024": """
        SELECT series_name, host_country, match_type, start_date, total_matches
        FROM series
        WHERE YEAR(start_date) = 2024;
    """,

    # Intermediate (Q9–Q16)
    "Q9: All-rounders (1000+ runs, 50+ wickets)": """
        SELECT player_name, total_runs, total_wickets, format
        FROM player_career_stats
        WHERE total_runs > 1000 AND total_wickets > 50;
    """,
    "Q10: Last 20 completed matches": """
        SELECT match_desc, team1, team2, winner, victory_margin, victory_type, venue_name
        FROM matches
        WHERE status = 'Completed'
        ORDER BY match_date DESC
        LIMIT 20;
    """,
    "Q11: Compare player performance across formats": """
        SELECT player_name,
               SUM(CASE WHEN format='Test' THEN total_runs ELSE 0 END) AS Test_Runs,
               SUM(CASE WHEN format='ODI' THEN total_runs ELSE 0 END) AS ODI_Runs,
               SUM(CASE WHEN format='T20I' THEN total_runs ELSE 0 END) AS T20_Runs,
               AVG(batting_avg) AS Overall_Avg
        FROM player_career_stats
        GROUP BY player_id, player_name
        HAVING COUNT(DISTINCT format) >= 2;
    """,
    "Q12: Team performance home vs away": """
        SELECT m.team1 AS team, 
               SUM(CASE WHEN m.country = p.country AND m.winner = m.team1 THEN 1 ELSE 0 END) AS home_wins,
               SUM(CASE WHEN m.country <> p.country AND m.winner = m.team1 THEN 1 ELSE 0 END) AS away_wins
        FROM matches m
        JOIN players p ON m.team1 = p.country
        GROUP BY m.team1;
    """,
    "Q13: Batting partnerships > 100 runs": """
        SELECT p1.player_name AS batsman1, p2.player_name AS batsman2,
               SUM(pm1.runs + pm2.runs) AS partnership_runs
        FROM player_match_stats pm1
        JOIN player_match_stats pm2 ON pm1.match_id = pm2.match_id AND pm1.id < pm2.id
        JOIN players p1 ON pm1.player_id = p1.player_id
        JOIN players p2 ON pm2.player_id = p2.player_id
        GROUP BY pm1.match_id, batsman1, batsman2
        HAVING partnership_runs >= 100;
    """,
    "Q14: Bowling performance by venue": """
        SELECT player_name, venue_name,
               AVG(runs_conceded/overs) AS avg_economy,
               SUM(wickets) AS total_wickets,
               COUNT(DISTINCT match_id) AS matches_played
        FROM player_match_stats
        JOIN matches m ON player_match_stats.match_id = m.match_id
        WHERE overs >= 4
        GROUP BY player_id, player_name, venue_name
        HAVING matches_played >= 3;
    """,
    "Q15: Players in close matches": """
        SELECT player_name,
               AVG(runs) AS avg_runs,
               COUNT(*) AS close_matches
        FROM player_match_stats pm
        JOIN matches m ON pm.match_id = m.match_id
        WHERE (m.victory_type = 'Runs' AND CAST(m.victory_margin AS UNSIGNED) < 50)
           OR (m.victory_type = 'Wickets' AND CAST(m.victory_margin AS UNSIGNED) < 5)
        GROUP BY player_id, player_name;
    """,
    "Q16: Batting performance by year since 2020": """
        SELECT player_name, YEAR(m.match_date) AS year,
               AVG(pm.runs) AS avg_runs,
               AVG((pm.runs/pm.balls)*100) AS avg_sr
        FROM player_match_stats pm
        JOIN matches m ON pm.match_id = m.match_id
        WHERE YEAR(m.match_date) >= 2020
        GROUP BY player_id, player_name, year
        HAVING COUNT(*) >= 5;
    """,

    # Advanced (Q17–Q25)
    "Q17: Toss impact on results": """
        SELECT toss_decision,
               SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) / COUNT(*) * 100 AS win_percentage
        FROM matches
        GROUP BY toss_decision;
    """,
    "Q18: Most economical bowlers (ODI/T20)": """
        SELECT player_name,
               SUM(runs_conceded)/SUM(overs) AS economy,
               SUM(wickets) AS total_wickets
        FROM player_match_stats
        WHERE format IN ('ODI','T20I')
        GROUP BY player_id, player_name
        HAVING COUNT(match_id) >= 10
        ORDER BY economy ASC
        LIMIT 10;
    """,
    "Q19: Consistent batsmen (low std dev)": """
        SELECT player_name,
               AVG(runs) AS avg_runs,
               STDDEV(runs) AS run_stddev
        FROM player_match_stats
        WHERE balls >= 10 AND YEAR(CURDATE()) >= 2022
        GROUP BY player_id, player_name
        HAVING COUNT(*) >= 5;
    """,
    "Q20: Player matches and averages across formats": """
        SELECT player_name,
               SUM(CASE WHEN format='Test' THEN 1 ELSE 0 END) AS Test_Matches,
               SUM(CASE WHEN format='ODI' THEN 1 ELSE 0 END) AS ODI_Matches,
               SUM(CASE WHEN format='T20I' THEN 1 ELSE 0 END) AS T20_Matches,
               AVG(batting_avg) AS avg_bat
        FROM player_career_stats
        GROUP BY player_id, player_name
        HAVING (Test_Matches+ODI_Matches+T20_Matches) >= 20;
    """,
    "Q21: Performance ranking system": """
        SELECT player_name,
               (total_runs*0.01 + batting_avg*0.5 + 80*0.3) +
               (total_wickets*2 + (50-batting_avg)*0.5 + (6-3)*2) AS score
        FROM player_career_stats
        ORDER BY score DESC
        LIMIT 10;
    """,
    "Q22: Head-to-head match analysis": """
        SELECT team1, team2,
               COUNT(*) AS matches_played,
               SUM(CASE WHEN winner=team1 THEN 1 ELSE 0 END) AS team1_wins,
               SUM(CASE WHEN winner=team2 THEN 1 ELSE 0 END) AS team2_wins
        FROM matches
        GROUP BY team1, team2
        HAVING matches_played >= 5;
    """,
    "Q23: Recent player form": """
        SELECT player_name,
               AVG(runs) AS avg_runs,
               SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END) AS scores_50_plus
        FROM player_match_stats
        GROUP BY player_id, player_name
        HAVING COUNT(*) >= 10;
    """,
    "Q24: Best batting partnerships": """
        SELECT pm1.player_name AS batsman1, pm2.player_name AS batsman2,
               AVG(pm1.runs+pm2.runs) AS avg_runs,
               MAX(pm1.runs+pm2.runs) AS highest_partnership
        FROM player_match_stats pm1
        JOIN player_match_stats pm2 ON pm1.match_id = pm2.match_id AND pm1.id < pm2.id
        GROUP BY batsman1, batsman2
        HAVING COUNT(*) >= 5;
    """,
    "Q25: Time series batting evolution": """
        SELECT player_name, YEAR(match_date) AS year, QUARTER(match_date) AS quarter,
               AVG(runs) AS avg_runs,
               AVG((runs/balls)*100) AS avg_sr
        FROM player_match_stats pm
        JOIN matches m ON pm.match_id=m.match_id
        GROUP BY player_id, player_name, year, quarter
        HAVING COUNT(*) >= 3;
    """
}

def app():
    st.title("📊 SQL Queries & Analytics")
    st.sidebar.header("Select Query")
    query_name = st.sidebar.selectbox("Choose one of 25 queries", list(QUERIES.keys()))

    st.subheader(query_name)
    sql = QUERIES[query_name]
    st.code(sql, language="sql")

    if st.button("Run Query"):
        df = run_query(sql)
        if df.empty:
            st.warning("⚠️ No data found or table missing.")
        else:
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    app()

