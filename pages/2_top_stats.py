import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Function to fetch top stats data from RapidAPI
def fetch_top_stats():
    url = "https://cricbuzz-cricket2.p.rapidapi.com/stats/v1/topstats"
    headers = {
        "x-rapidapi-key": "a939ac6cafmsh8a08624b2a5dacdp10cb99jsn689b0f4c2adb",  # Replace with your actual key if needed
        "x-rapidapi-host": "cricbuzz-cricket2.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return None

# Main function for the Top Player Stats page
def top_player_stats_page():
    st.title("Top Player Stats")
    st.markdown("Explore the top batting and bowling statistics in cricket, visualized for clarity.")

    # Fetch data
    data = fetch_top_stats()
    if data is None:
        return

    # Assuming the JSON structure has keys like 'batting' and 'bowling', each with lists of stats
    # Adjust based on actual API response. Example assumed structure:
    # {
    #   "batting": [
    #     {"category": "most_runs", "players": [{"name": "Player1", "value": 10000}, ...]},
    #     {"category": "highest_score", "players": [{"name": "Player2", "value": 400}, ...]}
    #   ],
    #   "bowling": [
    #     {"category": "most_wickets", "players": [{"name": "Player3", "value": 500}, ...]},
    #     ...
    #   ]
    # }
    # If the structure differs, inspect the printed JSON and modify accordingly.

    # Process batting stats
    if "batting" in data:
        st.header("Top Batting Stats")
        for stat in data["batting"]:
            category = stat.get("category", "Unknown").replace("_", " ").title()
            players = stat.get("players", [])
            if players:
                df = pd.DataFrame(players)
                df.columns = ["Player", "Value"]  # Rename columns for clarity
                
                # Display table
                st.subheader(f"{category}")
                st.dataframe(df, use_container_width=True)
                
                # Visualize as bar chart
                fig = px.bar(df, x="Player", y="Value", title=f"{category} - Top Players", 
                             labels={"Value": category.replace(" ", "")})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write(f"No data available for {category}.")

    # Process bowling stats
    if "bowling" in data:
        st.header("Top Bowling Stats")
        for stat in data["bowling"]:
            category = stat.get("category", "Unknown").replace("_", " ").title()
            players = stat.get("players", [])
            if players:
                df = pd.DataFrame(players)
                df.columns = ["Player", "Value"]
                
                # Display table
                st.subheader(f"{category}")
                st.dataframe(df, use_container_width=True)
                
                # Visualize as bar chart
                fig = px.bar(df, x="Player", y="Value", title=f"{category} - Top Players", 
                             labels={"Value": category.replace(" ", "")})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write(f"No data available for {category}.")

    # Add a note if no data
    if not data.get("batting") and not data.get("bowling"):
        st.write("No stats data available.")

# Run the page (integrate this into your main Streamlit app)
if __name__ == "__main__":
    top_player_stats_page()
