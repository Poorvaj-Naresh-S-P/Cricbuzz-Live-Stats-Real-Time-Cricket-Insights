import requests
import streamlit as st

API_KEY = "241cbfdb81mshf7f104545e0f7b2p18118ejsn97a7eadb6ac8"

def live_matches_page():
	def fetch_matches(endpoint: str):
	    url = f"https://cricbuzz-cricket2.p.rapidapi.com/matches/v1/{endpoint}"
	    headers = {
		"x-rapidapi-key": API_KEY,
		"x-rapidapi-host": "cricbuzz-cricket2.p.rapidapi.com"
	    }
	    resp = requests.get(url, headers=headers)
	    if resp.status_code == 200:
	        return resp.json()
	    else:
	        st.error(f"Error fetching {endpoint} matches: {resp.status_code}")
	        return None
	
	def render_matches(data):
	    if data and "typeMatches" in data:
	        for match_type in data["typeMatches"]:
	            st.header(f"📌 {match_type['matchType']} Matches")
	
	            for series in match_type.get("seriesMatches", []):
	                if "seriesAdWrapper" in series:
	                    series_name = series["seriesAdWrapper"].get("seriesName", "Unknown Series")
	                    st.subheader(series_name)
	
	                    for match in series["seriesAdWrapper"].get("matches", []):
	                        info = match.get("matchInfo", {})
	                        score = match.get("matchScore", {})
	
	                        team1 = info.get("team1", {}).get("teamName", "TBD")
	                        team2 = info.get("team2", {}).get("teamName", "TBD")
	                        status = info.get("status", "No Status")
	                        venue = info.get("venueInfo", {}).get("ground", "Unknown Venue")
	
	                        team1_runs = score.get("team1Score", {}).get("inngs1", {}).get("runs", "-")
	                        team1_wkts = score.get("team1Score", {}).get("inngs1", {}).get("wickets", "-")
	                        team2_runs = score.get("team2Score", {}).get("inngs1", {}).get("runs", "-")
	                        team2_wkts = score.get("team2Score", {}).get("inngs1", {}).get("wickets", "-")
	
	                        with st.container():
	                            st.markdown(
	                                f"""
	                                <div style="border-radius:10px; padding:12px; margin:10px 0;
	                                            background-color:#f9f9f9; box-shadow:2px 2px 10px rgba(0,0,0,0.1);">
	                                    <h4 style="margin:0;">{team1} 🆚 {team2}</h4>
	                                    <p style="margin:2px 0; color:blue;">🏟 {venue}</p>
	                                    <p style="margin:2px 0;"><b>Status:</b> {status}</p>
	                                    <p style="margin:2px 0;">
	                                        <b>{team1}</b>: {team1_runs}/{team1_wkts} &nbsp;&nbsp;
	                                        <b>{team2}</b>: {team2_runs}/{team2_wkts}
	                                    </p>
	                                </div>
	                                """,
	                                unsafe_allow_html=True
	                            )
	    else:
	        st.warning("No matches available in this section.")
	
	tab1, tab2, tab3 = st.tabs(["🔴 Live", "📜 Recent", "⏳ Upcoming"])
	
	with tab1:
	    live_data = fetch_matches("live")
	    render_matches(live_data)
	
	with tab2:
	    recent_data = fetch_matches("recent")
	    render_matches(recent_data)
	
	with tab3:
	    upcoming_data = fetch_matches("upcoming")
	    render_matches(upcoming_data)


