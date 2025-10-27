import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time

@st.cache_data  # Cache to avoid repeated calls
def fetch_stats(endpoint: str, format_type: str, retries=3):
    API_KEY = "a81164e5afmsh5877b527597273ap137de8jsn722347f07f4f"
    url = f"https://cricbuzz-cricket2.p.rapidapi.com/stats/v1/rankings/{endpoint}"
    querystring = {"isWomen": "0", "formatType": format_type.lower()}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "cricbuzz-cricket2.p.rapidapi.com"
    }
    
    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            if attempt < retries - 1:
                st.warning(f"Rate limit hit for {endpoint} ({format_type}). Retrying in 1 second...")
                time.sleep(1)  # Wait 1 second before retry
            else:
                st.error(f"Rate limit exceeded for {endpoint} ({format_type}). Try again later or upgrade your API plan.")
                return None
        else:
            st.error(f"Error fetching {endpoint} for {format_type}: {response.status_code}")
            return None
    return None

# Main page function for ICC Rankings
def icc_rankings_page():
    st.title("ICC Player Rankings")
    st.markdown("Explore top ICC rankings for batsmen and bowlers across formats, with clean lists, tables, and charts.")

    # Tabs for formats
    tab_t20, tab_odi, tab_test = st.tabs(["T20", "ODI", "Test"])

    # Helper function to display rankings
    def display_rankings(format_type: str):
        st.header(f"{format_type.upper()} Rankings")
        
        # Fetch and display batsmen
        batsmen_data = fetch_stats("batsmen", format_type)
        if batsmen_data and isinstance(batsmen_data, dict) and 'rank' in batsmen_data:
            df_batsmen = pd.DataFrame(batsmen_data['rank'])
            df_batsmen = df_batsmen[['rank', 'name', 'country', 'rating', 'trend']].copy()
            df_batsmen['rank'] = df_batsmen['rank'].astype(int)
            df_batsmen = df_batsmen.sort_values('rank').head(10)
            
            # Layout: Columns for rank list and visualizations
            col1, col2 = st.columns([1, 2])  # Left: Rank list, Right: Table/Chart
            
            with col1:
                st.subheader("Top Batsmen Rank List")
                for _, row in df_batsmen.iterrows():
                    trend_icon = "⬆️" if row['trend'] == 'Up' else "⬇️" if row['trend'] == 'Down' else "➡️"
                    st.write(f"{int(row['rank'])}. {row['name']} ({row['country']}) - Rating: {row['rating']} {trend_icon}")
            
            with col2:
                st.subheader("Batsmen Table & Charts")
                st.dataframe(df_batsmen[['rank', 'name', 'country', 'rating', 'trend']], use_container_width=True)
                
                # Vertical bar chart
                fig_bar = px.bar(df_batsmen, x='name', y='rating', title=f"Top {format_type} Batsmen Ratings",
                                 labels={'rating': 'Rating', 'name': 'Player'}, color='trend',
                                 color_discrete_map={'Up': 'green', 'Down': 'red', 'Flat': 'gray'})
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Horizontal bar chart for cleaner view
                fig_hbar = px.bar(df_batsmen, y='name', x='rating', orientation='h', title=f"Horizontal View - {format_type} Batsmen",
                                  labels={'rating': 'Rating', 'name': 'Player'}, color='trend',
                                  color_discrete_map={'Up': 'green', 'Down': 'red', 'Flat': 'gray'})
                st.plotly_chart(fig_hbar, use_container_width=True)
        else:
            st.write("No batsmen data available.")
        
        # Fetch and display bowlers (similar structure)
        bowlers_data = fetch_stats("bowlers", format_type)
        if bowlers_data and isinstance(bowlers_data, dict) and 'rank' in bowlers_data:
            df_bowlers = pd.DataFrame(bowlers_data['rank'])
            df_bowlers = df_bowlers[['rank', 'name', 'country', 'rating', 'trend']].copy()
            df_bowlers['rank'] = df_bowlers['rank'].astype(int)
            df_bowlers = df_bowlers.sort_values('rank').head(10)
            
            # Layout: Columns
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Top Bowlers Rank List")
                for _, row in df_bowlers.iterrows():
                    trend_icon = "⬆️" if row['trend'] == 'Up' else "⬇️" if row['trend'] == 'Down' else "➡️"
                    st.write(f"{int(row['rank'])}. {row['name']} ({row['country']}) - Rating: {row['rating']} {trend_icon}")
            
            with col2:
                st.subheader("Bowlers Table & Charts")
                st.dataframe(df_bowlers[['rank', 'name', 'country', 'rating', 'trend']], use_container_width=True)
                
                # Vertical bar chart
                fig_bar = px.bar(df_bowlers, x='name', y='rating', title=f"Top {format_type} Bowlers Ratings",
                                 labels={'rating': 'Rating', 'name': 'Player'}, color='trend',
                                 color_discrete_map={'Up': 'green', 'Down': 'red', 'Flat': 'gray'})
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Horizontal bar chart
                fig_hbar = px.bar(df_bowlers, y='name', x='rating', orientation='h', title=f"Horizontal View - {format_type} Bowlers",
                                  labels={'rating': 'Rating', 'name': 'Player'}, color='trend',
                                  color_discrete_map={'Up': 'green', 'Down': 'red', 'Flat': 'gray'})
                st.plotly_chart(fig_hbar, use_container_width=True)
        else:
            st.write("No bowlers data available.")

    # Populate tabs
    with tab_t20:
        display_rankings("t20")
    with tab_odi:
        display_rankings("odi")
    with tab_test:
        display_rankings("test")

icc_rankings_page()
