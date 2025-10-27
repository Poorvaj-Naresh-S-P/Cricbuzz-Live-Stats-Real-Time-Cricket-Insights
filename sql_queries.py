import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

def sql_queries_page():
    st.set_page_config(layout="wide", page_title="Cricket SQL & Analytics (MySQL)")
    
    st.title("Cricket SQL & Analytics — Q1 to Q25 (best-effort)")
    
    # -------------------------
    # MySQL Connection UI
    # -------------------------
    st.sidebar.header("MySQL Connection")
    host = st.sidebar.text_input("Host", "localhost")
    port = st.sidebar.text_input("Port", "3306")
    user = st.sidebar.text_input("User", "root")
    password = st.sidebar.text_input("Password", "", type="password")
    database = st.sidebar.text_input("Database", "cricket")
    
    # Connect/engine factory
    def get_engine():
        conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        return create_engine(conn_str, pool_pre_ping=True)
    
    st.sidebar.markdown("Click below to check connection")
    if st.sidebar.button("Test Connection"):
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            st.sidebar.success("Connection OK")
        except Exception as e:
            st.sidebar.error(f"Connection failed: {e}")
    
    # -------------------------
    # Helper functions
    # -------------------------
    def table_exists(engine, table):
        try:
            with engine.connect() as conn:
                r = conn.execute(text("SHOW TABLES LIKE :t"), {"t": table})
                return r.fetchone() is not None
        except Exception:
            return False
    
    def load_table(engine, name):
        try:
            if table_exists(engine, name):
                return pd.read_sql_table(name, engine)
        except Exception:
            # fallback to reading via SQL if naming differences:
            try:
                return pd.read_sql(f"SELECT * FROM `{name}` LIMIT 100000", engine)
            except Exception:
                return pd.DataFrame()
        return pd.DataFrame()
    
    def has_cols(df, cols):
        if df is None or df.empty:
            return False
        for c in cols:
            if c not in df.columns:
                return False
        return True
    
    # Main runner: implements Q1..Q25 using loaded DataFrames (best-effort)
    def run_questions(engine):
        out = []
        now = datetime.now()
    
        # load common tables (lowercase names as common)
        players = load_table(engine, "player")
        if players.empty:
            players = load_table(engine, "players")  # try plural
    
        matches = load_table(engine, "matches")
        venues = load_table(engine, "venues")
        series = load_table(engine, "series")
        performances = load_table(engine, "performances")
        partnerships = load_table(engine, "partnerships")
        teams = load_table(engine, "teams")
    
        # ensure we have DataFrames (maybe empty)
        dfs = {
            "players": players,
            "matches": matches,
            "venues": venues,
            "series": series,
            "performances": performances,
            "partnerships": partnerships,
            "teams": teams
        }
    
        # Q1: Players from India
        if has_cols(players, ["country","full_name"]) or has_cols(players, ["country","name"]):
            name_col = "full_name" if "full_name" in players.columns else ("name" if "name" in players.columns else players.columns[0])
            role_cols = []
            for c in ["playing_role","batting_style","bowling_style"]:
                if c not in players.columns:
                    players[c] = None
                role_cols.append(c)
            q1 = players[players["country"].str.lower()=="india"].loc[:, [name_col]+role_cols].rename(columns={name_col:"player_name"})
            out.append(("Q1 Players from India", q1))
        else:
            out.append(("Q1 Players from India", pd.DataFrame({"info":["Need table 'player(s)' with columns: country, full_name/name"]})))
    
        # Q2: Recent matches (last 7 days)
        if has_cols(matches, ["date","team1","team2"]):
            matches["date_parsed"] = pd.to_datetime(matches["date"], errors="coerce")
            cutoff = now - timedelta(days=7)
            recent = matches[matches["date_parsed"] >= cutoff].sort_values("date_parsed", ascending=False)
            cols = [c for c in ["description","team1","team2","venue_name","venue_city","date"] if c in recent.columns]
            if cols:
                out.append(("Q2 Recent matches (last 7 days)", recent[cols].head(200)))
            else:
                out.append(("Q2 Recent matches (last 7 days)", pd.DataFrame({"info":["matches table present but lacks descriptive columns like description/venue_name/venue_city"]})))
        else:
            out.append(("Q2 Recent matches (last 7 days)", pd.DataFrame({"info":["Need 'matches' with date, team1, team2"]})))
    
        # Q3: Top 10 ODI run scorers
        # Try players table for ODI runs column; fallback to performances filtered by format
        odicol = None
        for c in players.columns:
            if "odi" in c.lower() and ("runs" in c.lower() or "runs" == c.lower()):
                odicol = c; break
        if odicol:
            df = players[[c for c in ["full_name", odicol] if c in players.columns]]
            df = df.rename(columns={odicol:"odi_runs"})
            df["odi_runs"] = pd.to_numeric(df["odi_runs"], errors="coerce").fillna(0)
            top = df.sort_values("odi_runs", ascending=False).head(10)
            out.append(("Q3 Top 10 ODI run scorers (from players)", top))
        elif has_cols(performances, ["format","player_name","runs"]):
            od = performances[performances["format"].str.lower()=="odi"]
            if not od.empty:
                agg = od.groupby("player_name").agg(odi_runs=("runs","sum"))
                # best-effort batting avg/centuries if columns exist
                if "average" in od.columns:
                    agg["bat_avg"] = od.groupby("player_name")["average"].mean()
                if "hundreds" in od.columns:
                    agg["hundreds"] = od.groupby("player_name")["hundreds"].sum()
                out.append(("Q3 Top 10 ODI run scorers (from performances)", agg.sort_values("odi_runs", ascending=False).head(10).reset_index()))
            else:
                out.append(("Q3 Top 10 ODI run scorers", pd.DataFrame({"info":["No ODI rows in performances table"]})))
        else:
            out.append(("Q3 Top 10 ODI run scorers", pd.DataFrame({"info":["Insufficient data: need players ODI columns or performances with format/runs"]})))
    
        # Q4: Venues capacity > 30000
        if has_cols(venues, ["capacity"]):
            venues["capacity_num"] = pd.to_numeric(venues["capacity"], errors="coerce").fillna(0)
            res = venues[venues["capacity_num"]>30000]
            cols = [c for c in ["name","city","country","capacity"] if c in venues.columns]
            out.append(("Q4 Venues capacity >30000", res[cols].sort_values("capacity_num", ascending=False)))
        else:
            out.append(("Q4 Venues capacity >30000", pd.DataFrame({"info":["Need 'venues' table with 'capacity'"]})))
    
        # Q5: Team wins count
        if has_cols(matches, ["winner"]):
            wins = matches.groupby("winner").size().reset_index(name="wins").sort_values("wins", ascending=False).rename(columns={"winner":"team"})
            out.append(("Q5 Team wins count", wins))
        elif has_cols(teams, ["team_name","wins"]):
            out.append(("Q5 Team wins count", teams[["team_name","wins"]].sort_values("wins", ascending=False)))
        else:
            out.append(("Q5 Team wins count", pd.DataFrame({"info":["Need matches.winner or teams.wins"]})))
    
        # Q6: Count by playing_role
        if has_cols(players, ["playing_role"]):
            role_counts = players["playing_role"].fillna("Unknown").value_counts().reset_index()
            role_counts.columns = ["role","count"]
            out.append(("Q6 Player counts by role", role_counts))
        else:
            out.append(("Q6 Player counts by role", pd.DataFrame({"info":["Need players.playing_role"]})))
    
        # Q7: Highest individual batting score per format
        if has_cols(performances, ["format","high_score"]):
            performances["high_score_num"] = pd.to_numeric(performances["high_score"].astype(str).str.replace("*","",regex=False), errors="coerce")
            q7 = performances.groupby("format")["high_score_num"].max().reset_index().rename(columns={"high_score_num":"highest_score"})
            out.append(("Q7 Highest score per format", q7))
        else:
            out.append(("Q7 Highest score per format", pd.DataFrame({"info":["Need performances.format & high_score"]})))
    
        # Q8: Series started in 2024
        if has_cols(series, ["start_date","name"]):
            series["start_parsed"] = pd.to_datetime(series["start_date"], errors="coerce")
            s2024 = series[series["start_parsed"].dt.year==2024]
            cols = [c for c in ["name","host_country","match_type","start_date","total_matches"] if c in s2024.columns]
            out.append(("Q8 Series started in 2024", s2024[cols]))
        else:
            out.append(("Q8 Series started in 2024", pd.DataFrame({"info":["Need series.start_date & name"]})))
    
        # Q9: All-rounders >1000 runs & >50 wickets (best-effort from performances)
        if has_cols(performances, ["player_name","runs","wickets"]):
            agg = performances.groupby("player_name").agg(total_runs=("runs","sum"), total_wickets=("wickets","sum")).reset_index()
            res = agg[(agg["total_runs"]>1000)&(agg["total_wickets"]>50)]
            out.append(("Q9 All-rounders >1000 runs & >50 wickets", res))
        else:
            out.append(("Q9 All-rounders >1000 runs & >50 wickets", pd.DataFrame({"info":["Need performances with player_name,runs,wickets"]})))
    
        # Q10: Last 20 completed matches
        if has_cols(matches, ["status","description","team1","team2","winner","result_margin","result_type","venue_name","date"]):
            completed = matches[matches["status"].str.lower().isin(["complete","finished","result","completed"]) | matches["winner"].notna()]
            completed["date_parsed"] = pd.to_datetime(completed["date"], errors="coerce")
            last20 = completed.sort_values("date_parsed", ascending=False).head(20)
            cols = [c for c in ["description","team1","team2","winner","result_margin","result_type","venue_name","date"] if c in last20.columns]
            out.append(("Q10 Last 20 completed matches", last20[cols]))
        else:
            out.append(("Q10 Last 20 completed matches", pd.DataFrame({"info":["Need matches with status/winner/result fields"]})))
    
        # Q11 Compare player across formats
        if has_cols(performances, ["player_name","format","runs"]):
            agg = performances.groupby(["player_name","format"]).agg(total_runs=("runs","sum"), matches=("match_id","nunique") if "match_id" in performances.columns else ("runs","count")).reset_index()
            pivot = agg.pivot(index="player_name", columns="format", values="total_runs").fillna(0)
            pivot["formats_played"] = (pivot>0).sum(axis=1)
            pivot = pivot[pivot["formats_played"]>=2]
            overall_avg = performances.groupby("player_name")["average"].mean().reset_index() if "average" in performances.columns else None
            res = pivot.reset_index()
            if overall_avg is not None:
                res = res.merge(overall_avg, left_on="player_name", right_on="player_name", how="left")
            out.append(("Q11 Player runs across formats (>=2 formats)", res))
        else:
            out.append(("Q11 Player runs across formats", pd.DataFrame({"info":["Need performances with player_name,format,runs"]})))
    
        # Q12 Home vs Away wins per team (best-effort)
        if has_cols(matches, ["team1","team2","venue_country","winner"]):
            if "team1_country" in matches.columns and "team2_country" in matches.columns:
                def home_away(row):
                    winner = row["winner"]
                    if pd.isna(winner): return None
                    if winner==row["team1"] and row["team1_country"]==row["venue_country"]:
                        return ("home", row["team1"])
                    if winner==row["team1"]:
                        return ("away", row["team1"])
                    if winner==row["team2"] and row["team2_country"]==row["venue_country"]:
                        return ("home", row["team2"])
                    if winner==row["team2"]:
                        return ("away", row["team2"])
                    return None
                ma = matches.apply(home_away, axis=1)
                info = [x for x in ma if x]
                if info:
                    df_ha = pd.DataFrame(info, columns=["home_away","team"])
                    res = df_ha.groupby(["team","home_away"]).size().unstack(fill_value=0).reset_index()
                    out.append(("Q12 Home vs Away wins (best-effort)", res))
                else:
                    out.append(("Q12 Home vs Away wins", pd.DataFrame({"info":["Unable to determine home/away from available fields"]})))
            else:
                out.append(("Q12 Home vs Away wins", pd.DataFrame({"info":["Need team1_country/team2_country & venue_country columns for robust home/away detection"]})))
        else:
            out.append(("Q12 Home vs Away wins", pd.DataFrame({"info":["Need matches with winner & venue_country"]})))
    
        # Q13 Partnerships >=100 (consecutive batsmen best-effort)
        if has_cols(partnerships, ["player1","player2","runs","innings_id"]):
            p = partnerships[partnerships["runs"]>=100].loc[:, ["player1","player2","runs","innings_id"]]
            out.append(("Q13 Partnerships >=100", p))
        else:
            out.append(("Q13 Partnerships >=100", pd.DataFrame({"info":["Need partnerships with player1,player2,runs,innings_id"]})))
    
        # Q14 Bowling performance at venues (best-effort)
        if has_cols(performances, ["player_name","venue","wickets","overs"]):
            df = performances.copy()
            df["overs_f"] = pd.to_numeric(df["overs"], errors="coerce")
            df_bow = df[df["overs_f"]>=4]
            agg = df_bow.groupby(["player_name","venue"]).agg(matches=("match_id","nunique") if "match_id" in df_bow.columns else ("overs_f","count"),
                                                            avg_econ=("economy","mean") if "economy" in df_bow.columns else ("wickets", lambda s: np.nan),
                                                            total_wickets=("wickets","sum")).reset_index()
            res = agg[agg["matches"]>=3]
            out.append(("Q14 Bowling by venue (best-effort)", res))
        else:
            out.append(("Q14 Bowling by venue", pd.DataFrame({"info":["Need performances with player_name,venue,overs,wickets"]})))
    
        # Q15 Close matches player stats
        if has_cols(matches, ["result_margin","result_type","match_id"]) and has_cols(performances, ["match_id","player_name","runs","team"]):
            m = matches.copy()
            def is_close(row):
                try:
                    rt = str(row.get("result_type","")).lower()
                    rm = float(row.get("result_margin") or 0)
                    if rt=="runs" and rm<50: return True
                    if rt=="wickets" and rm<5: return True
                    return False
                except:
                    return False
            m["is_close"] = m.apply(is_close, axis=1)
            close_ids = m[m["is_close"]==True]["match_id"].unique().tolist()
            perf_c = performances[performances["match_id"].isin(close_ids)]
            if not perf_c.empty:
                agg = perf_c.groupby("player_name").agg(avg_runs=("runs","mean"), close_matches=("match_id","nunique"))
                merged = perf_c.merge(matches[["match_id","winner"]], on="match_id", how="left")
                won = merged[merged["team"]==merged["winner"]].groupby("player_name").size().reset_index(name="wins_when_batting")
                agg = agg.reset_index().merge(won, on="player_name", how="left").fillna(0)
                out.append(("Q15 Close matches player stats", agg.sort_values("avg_runs", ascending=False).reset_index(drop=True)))
            else:
                out.append(("Q15 Close matches player stats", pd.DataFrame({"info":["No close match performances found"]})))
        else:
            out.append(("Q15 Close matches player stats", pd.DataFrame({"info":["Need matches and performances with required columns"]})))
    
        # Q16 Year-by-year since 2020: avg runs & strike rate per player (>=5 matches)
        if has_cols(performances, ["player_name","date","runs","strike_rate","match_id"]):
            perf = performances.copy()
            perf["date_parsed"] = pd.to_datetime(perf["date"], errors="coerce")
            perf_2020 = perf[perf["date_parsed"].dt.year>=2020].copy()
            perf_2020["year"] = perf_2020["date_parsed"].dt.year
            agg = perf_2020.groupby(["player_name","year"]).agg(matches=("match_id","nunique"), avg_runs=("runs","mean"), avg_sr=("strike_rate","mean")).reset_index()
            res = agg[agg["matches"]>=5].sort_values(["player_name","year"])
            out.append(("Q16 Yearly player batting (>5 matches/year)", res))
        else:
            out.append(("Q16 Yearly player batting (>5 matches/year)", pd.DataFrame({"info":["Need performances with date,runs,strike_rate,match_id"]})))
    
        # Q17 Toss advantage by decision
        if has_cols(matches, ["toss_winner","toss_decision","winner"]):
            df = matches.copy()
            df["won_after_toss"] = (df["toss_winner"]==df["winner"])
            report = df.groupby(["toss_decision"]).apply(lambda g: pd.Series({
                "matches": len(g),
                "wins_by_toss_winner": int(g["won_after_toss"].sum()),
                "pct_wins_by_toss_winner": float(g["won_after_toss"].mean()*100)
            })).reset_index()
            out.append(("Q17 Toss advantage by decision", report))
        else:
            out.append(("Q17 Toss advantage by decision", pd.DataFrame({"info":["Need matches.toss_winner,toss_decision,winner"]})))
    
        # Q18 Economical bowlers ODI/T20 (best-effort)
        if has_cols(performances, ["player_name","format","overs","economy","wickets","match_id"]):
            df = performances.copy()
            df["overs_f"] = pd.to_numeric(df["overs"], errors="coerce").fillna(0)
            agg = df.groupby(["player_name","format"]).agg(matches=("match_id","nunique"), total_overs=("overs_f","sum"), avg_overs_per_match=("overs_f", lambda s: s.sum()/s.nunique()), economy=("economy","mean"), total_wickets=("wickets","sum")).reset_index()
            cond = (agg["format"].str.lower().isin(["odi","t20","t20i"])) & (agg["matches"]>=10) & (agg["avg_overs_per_match"]>=2)
            res = agg[cond].sort_values("economy").reset_index(drop=True)
            out.append(("Q18 Economical bowlers (ODI/T20) best-effort", res))
        else:
            out.append(("Q18 Economical bowlers (ODI/T20)", pd.DataFrame({"info":["Need performances with overs,economy,wickets,match_id,format"]})))
    
        # Q19 Consistency (avg & std) best-effort since 2022, faced>=10 balls
        if has_cols(performances, ["player_name","runs","balls","date"]):
            df = performances.copy()
            df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
            df2 = df[df["date_parsed"].dt.year>=2022]
            df2 = df2[df2["balls"].fillna(0)>=10]
            agg = df2.groupby("player_name").agg(avg_runs=("runs","mean"), std_runs=("runs","std"), innings=("runs","count")).reset_index()
            agg = agg[agg["innings"]>=1]
            out.append(("Q19 Consistency (avg & std) best-effort", agg.sort_values("std_runs").reset_index(drop=True)))
        else:
            out.append(("Q19 Consistency (avg & std)", pd.DataFrame({"info":["Need performances with runs,balls,date"]})))
    
        # Q20 Matches per format + batting avg for players with >=20 matches
        if has_cols(performances, ["player_name","format","match_id","runs"]):
            agg = performances.groupby(["player_name","format"]).agg(matches=("match_id","nunique"), avg_runs=("runs","mean")).reset_index()
            total = agg.groupby("player_name")["matches"].sum().reset_index(name="total_matches")
            merged = agg.merge(total, on="player_name")
            res = merged[merged["total_matches"]>=20].sort_values(["player_name","format"])
            out.append(("Q20 Matches per format & batting avg (players >=20 matches)", res))
        else:
            out.append(("Q20 Matches per format & batting avg", pd.DataFrame({"info":["Need performances with player_name,format,match_id,runs"]})))
    
        # Q21 Performance ranking (best-effort)
        if has_cols(performances, ["player_name"]):
            agg = performances.groupby("player_name").agg(
                runs=("runs","sum"),
                batting_avg=("average","mean") if "average" in performances.columns else ("runs", lambda s: np.nan),
                strike_rate=("strike_rate","mean") if "strike_rate" in performances.columns else ("runs", lambda s: np.nan),
                wickets=("wickets","sum") if "wickets" in performances.columns else ("runs", lambda s: 0),
                bowling_avg=("bowling_average","mean") if "bowling_average" in performances.columns else ("wickets", lambda s: np.nan),
                economy=("economy","mean") if "economy" in performances.columns else ("wickets", lambda s: np.nan),
                catches=("catches","sum") if "catches" in performances.columns else ("runs", lambda s: 0),
                stumpings=("stumpings","sum") if "stumpings" in performances.columns else ("runs", lambda s: 0)
            ).reset_index()
            def safe(x): return 0 if pd.isna(x) else x
            agg["bat_points"] = agg.apply(lambda r: safe(r["runs"])*0.01 + safe(r["batting_avg"])*0.5 + safe(r["strike_rate"])*0.3, axis=1)
            agg["bowl_points"] = agg.apply(lambda r: safe(r["wickets"])*2 + (50 - safe(r["bowling_avg"]))*0.5 + (6 - safe(r["economy"]))*2, axis=1)
            agg["field_points"] = agg["catches"] + agg["stumpings"]
            agg["total_score"] = agg["bat_points"] + agg["bowl_points"] + agg["field_points"]
            out.append(("Q21 Player ranking (best-effort)", agg.sort_values("total_score", ascending=False).head(50)))
        else:
            out.append(("Q21 Player ranking", pd.DataFrame({"info":["Need performances table"]})))
    
        # Q22 Head-to-head last 3 years (>=5 matches)
        if has_cols(matches, ["team1","team2","date","winner","result_margin","result_type","venue_name"]):
            matches["date_parsed"] = pd.to_datetime(matches["date"], errors="coerce")
            cutoff = now - timedelta(days=3*365)
            recent = matches[matches["date_parsed"]>=cutoff]
            def pair_key(r):
                a,b = r["team1"], r["team2"]
                return tuple(sorted([a,b]))
            recent["pair"] = recent.apply(pair_key, axis=1)
            groups = recent.groupby("pair")
            rows = []
            for pair, g in groups:
                if len(g) < 5: continue
                t1, t2 = pair
                wins_t1 = (g["winner"]==t1).sum()
                wins_t2 = (g["winner"]==t2).sum()
                avg_margin_t1 = pd.to_numeric(g[g["winner"]==t1]["result_margin"], errors="coerce").astype(float).mean()
                avg_margin_t2 = pd.to_numeric(g[g["winner"]==t2]["result_margin"], errors="coerce").astype(float).mean()
                rows.append({"team_a":t1,"team_b":t2,"matches":len(g),"wins_a":int(wins_t1),"wins_b":int(wins_t2),
                             "avg_margin_a":float(avg_margin_t1 if not np.isnan(avg_margin_t1) else 0),
                             "avg_margin_b":float(avg_margin_t2 if not np.isnan(avg_margin_t2) else 0)})
            out.append(("Q22 Head-to-head (last 3 years, >=5 matches)", pd.DataFrame(rows)))
        else:
            out.append(("Q22 Head-to-head", pd.DataFrame({"info":["Need matches with team1/team2/date/winner"]})))
    
        # Q23 Recent form last 10 innings per player
        if has_cols(performances, ["player_name","date","runs","strike_rate"]):
            df = performances.copy()
            df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
            players_stats = []
            for p, g in df.sort_values("date_parsed", ascending=False).groupby("player_name"):
                last10 = g.head(10)
                if last10.empty: continue
                avg5 = last10.head(5)["runs"].mean()
                avg10 = last10["runs"].mean()
                sr5 = last10.head(5)["strike_rate"].mean() if "strike_rate" in last10.columns else np.nan
                sr10 = last10["strike_rate"].mean() if "strike_rate" in last10.columns else np.nan
                scores_above50 = (last10["runs"]>=50).sum()
                consistency = last10["runs"].std()
                score = ( (0 if np.isnan(avg5) else avg5)*0.6 + (0 if np.isnan(avg10) else avg10)*0.4 ) - (0.5*(consistency if not np.isnan(consistency) else 0))
                if score>60: form="Excellent"
                elif score>40: form="Good"
                elif score>20: form="Average"
                else: form="Poor"
                players_stats.append({"player":p,"avg5":avg5,"avg10":avg10,"sr5":sr5,"sr10":sr10,"50s_last10":int(scores_above50),"std_runs":float(consistency if not np.isnan(consistency) else 0),"form":form})
            out.append(("Q23 Recent form (last 10 performances) categorization", pd.DataFrame(players_stats)))
        else:
            out.append(("Q23 Recent form", pd.DataFrame({"info":["Need performances with date,runs,strike_rate"]})))
    
        # Q24 Batting partnerships stats
        if has_cols(partnerships, ["player1","player2","runs"]):
            p = partnerships.copy()
            p["pair_key"] = p.apply(lambda r: "|".join(sorted([str(r["player1"]), str(r["player2"])])), axis=1)
            agg = p.groupby("pair_key").agg(count=("runs","count"), avg_runs=("runs","mean"), fifty_plus=("runs", lambda s: (s>50).sum()), max_runs=("runs","max")).reset_index()
            res = agg[agg["count"]>=5].sort_values("avg_runs", ascending=False)
            out.append(("Q24 Successful batting partnerships", res))
        else:
            out.append(("Q24 Partnerships", pd.DataFrame({"info":["Need partnerships with player1,player2,runs"]})))
    
        # Q25 Quarterly time-series per player (best-effort)
        if has_cols(performances, ["player_name","date","runs","strike_rate"]):
            df = performances.copy()
            df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date_parsed"])
            df["quarter"] = df["date_parsed"].dt.to_period("Q")
            grouped = df.groupby(["player_name","quarter"]).agg(matches=("match_id","nunique") if "match_id" in df.columns else ("runs","count"), avg_runs=("runs","mean"), avg_sr=("strike_rate","mean")).reset_index()
            players_list = []
            for p, g in grouped.groupby("player_name"):
                if len(g)>=6 and (g["matches"].mean()>=3):
                    g_sorted = g.sort_values("quarter")
                    g_sorted["avg_runs_prev"] = g_sorted["avg_runs"].shift(1)
                    g_sorted["delta"] = g_sorted["avg_runs"] - g_sorted["avg_runs_prev"]
                    improving = (g_sorted["delta"]>0).sum()
                    declining = (g_sorted["delta"]<0).sum()
                    if improving > declining: traj="Career Ascending"
                    elif declining > improving: traj="Career Declining"
                    else: traj="Career Stable"
                    players_list.append({"player":p, "quarters":len(g), "avg_matches_per_quarter":float(g["matches"].mean()), "trajectory":traj})
            out.append(("Q25 Quarterly performance & trajectory", pd.DataFrame(players_list)))
        else:
            out.append(("Q25 Quarterly performance", pd.DataFrame({"info":["Need performances with date,runs,strike_rate"]})))
    
        return out
    
    # -------------------------
    # UI: Run button & display
    # -------------------------
    st.markdown("---")
    st.subheader("Run Q1–Q25 (best-effort)")
    engine = None
    try:
        engine = get_engine()
    except Exception as e:
        st.error(f"Unable to create engine (check credentials): {e}")
    
    if st.button("Run Q1–Q25 (best-effort)"):
        if engine is None:
            st.error("Database engine unavailable. Check MySQL connection on the left.")
        else:
            with st.spinner("Running analytics... this may take a few seconds"):
                results = run_questions(engine)
            for title, df in results:
                st.markdown(f"### {title}")
                if df is None or df.empty:
                    st.write("No result / insufficient data for this question.")
                else:
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode()
                    st.download_button(f"Download CSV — {title}", csv, file_name=f"{title.replace(' ','_')}.csv")
    
    # -------------------------
    # Custom SQL runner
    # -------------------------
    st.markdown("---")
    st.subheader("Run custom SQL on MySQL")
    sql = st.text_area("SQL", value="SHOW TABLES;", height=120)
    if st.button("Run SQL"):
        if engine is None:
            st.error("Database engine unavailable. Check MySQL connection on the left.")
        else:
            try:
                df_sql = pd.read_sql(sql, engine)
                st.dataframe(df_sql)
                st.download_button("Download result CSV", df_sql.to_csv(index=False).encode(), file_name="sql_result.csv")
            except Exception as e:
                st.error(f"SQL error: {e}")
    
    st.markdown(
        """
        **Notes & tips:**  
        - This app is adaptive: each question runs only if required tables/columns exist.  
        - Common table names expected: `player`/`players`, `matches`, `venues`, `series`, `performances`, `partnerships`, `teams`.  
        - If your table column names differ, either rename columns or paste a sample of one table (via the custom SQL box) and I'll adapt queries specifically.  
        - Want visual charts? Tell me which questions to visualize (I can add Plotly/Altair charts).  
        """
    )
    
