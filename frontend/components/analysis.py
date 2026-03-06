"""
Match analysis component - COMPLETELY REWRITTEN
Handles cricsummary properly with fallback methods
"""
import streamlit as st
import os
import tempfile
from pathlib import Path
from backend.match_service import MatchService
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import json


def create_manual_scorecard(match_data, team_number):
    """Create scorecard manually from JSON data"""
    try:
        innings = match_data.get('innings', [])
        
        if team_number > len(innings):
            return None
        
        target_inning = innings[team_number - 1]
        team_name = target_inning.get('team', 'Unknown')
        
        # Collect batting data
        batsman_data = {}
        bowler_data = {}
        
        for over in target_inning.get('overs', []):
            for delivery in over.get('deliveries', []):
                batter = delivery.get('batter', 'Unknown')
                bowler = delivery.get('bowler', 'Unknown')
                runs = delivery.get('runs', {})
                
                # Batting stats
                if batter not in batsman_data:
                    batsman_data[batter] = {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'out': False}
                
                batter_runs = runs.get('batter', 0)
                batsman_data[batter]['runs'] += batter_runs
                batsman_data[batter]['balls'] += 1
                
                if batter_runs == 4:
                    batsman_data[batter]['fours'] += 1
                elif batter_runs == 6:
                    batsman_data[batter]['sixes'] += 1
                
                # Check wicket
                wickets = delivery.get('wickets', [])
                if wickets:
                    for wicket in wickets:
                        if wicket.get('player_out') == batter:
                            batsman_data[batter]['out'] = True
                
                # Bowling stats
                if bowler not in bowler_data:
                    bowler_data[bowler] = {'runs': 0, 'wickets': 0, 'balls': 0}
                
                bowler_data[bowler]['runs'] += runs.get('total', 0)
                bowler_data[bowler]['balls'] += 1
                
                if wickets:
                    bowler_data[bowler]['wickets'] += len(wickets)
        
        # Create batting DataFrame
        batting_rows = []
        for batter, stats in batsman_data.items():
            sr = (stats['runs'] / stats['balls'] * 100) if stats['balls'] > 0 else 0
            batting_rows.append({
                'Batsman': batter,
                'Runs': stats['runs'],
                'Balls': stats['balls'],
                'Fours': stats['fours'],
                'Sixes': stats['sixes'],
                'Strike Rate': round(sr, 2),
                'Dismissed': 'Yes' if stats['out'] else 'No'
            })
        
        batting_df = pd.DataFrame(batting_rows)
        batting_df = batting_df.sort_values('Runs', ascending=False)
        
        # Create bowling DataFrame
        bowling_rows = []
        for bowler, stats in bowler_data.items():
            overs = stats['balls'] // 6
            balls_remaining = stats['balls'] % 6
            overs_str = f"{overs}.{balls_remaining}"
            economy = (stats['runs'] / (stats['balls'] / 6)) if stats['balls'] > 0 else 0
            
            bowling_rows.append({
                'Bowler': bowler,
                'Overs': overs_str,
                'Runs': stats['runs'],
                'Wickets': stats['wickets'],
                'Economy': round(economy, 2)
            })
        
        bowling_df = pd.DataFrame(bowling_rows)
        bowling_df = bowling_df.sort_values('Wickets', ascending=False)
        
        return {'batting': batting_df, 'bowling': bowling_df, 'team': team_name}
        
    except Exception as e:
        st.error(f"Error creating scorecard: {str(e)}")
        return None


def create_manual_extras(match_data, team_number):
    """Create extras breakdown manually"""
    try:
        innings = match_data.get('innings', [])
        if team_number > len(innings):
            return None
        
        target_inning = innings[team_number - 1]
        
        extras_data = {'wides': 0, 'noballs': 0, 'byes': 0, 'legbyes': 0, 'penalty': 0}
        
        for over in target_inning.get('overs', []):
            for delivery in over.get('deliveries', []):
                extras = delivery.get('extras', {})
                for extra_type in extras_data.keys():
                    if extra_type in extras:
                        extras_data[extra_type] += extras[extra_type]
        
        df = pd.DataFrame([extras_data])
        df['Total Extras'] = df.sum(axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error creating extras: {str(e)}")
        return None


def create_manual_fall_of_wickets(match_data, team_number):
    """Create fall of wickets manually"""
    try:
        innings = match_data.get('innings', [])
        if team_number > len(innings):
            return None
        
        target_inning = innings[team_number - 1]
        
        fow_data = []
        total_runs = 0
        wicket_number = 0
        
        for over in target_inning.get('overs', []):
            over_num = over.get('over', 0)
            for delivery in over.get('deliveries', []):
                total_runs += delivery.get('runs', {}).get('total', 0)
                
                wickets = delivery.get('wickets', [])
                if wickets:
                    for wicket in wickets:
                        wicket_number += 1
                        fow_data.append({
                            'Wicket': f"{wicket_number}",
                            'Player Out': wicket.get('player_out', 'Unknown'),
                            'Score': total_runs,
                            'Over': over_num,
                            'How Out': wicket.get('kind', 'Unknown')
                        })
        
        if fow_data:
            return pd.DataFrame(fow_data)
        else:
            return pd.DataFrame({'Message': ['No wickets fell']})
    except Exception as e:
        st.error(f"Error creating fall of wickets: {str(e)}")
        return None


def create_worm_chart(match_data):
    """Create worm chart manually"""
    try:
        innings = match_data.get('innings', [])
        
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('#1e293b')
        ax.set_facecolor('#0f172a')
        
        colors = ['#22d3ee', '#10b981']
        
        for idx, inning in enumerate(innings[:2]):  # Only first 2 innings
            team_name = inning.get('team', f'Team {idx+1}')
            cumulative_runs = []
            over_numbers = []
            
            total_runs = 0
            for over in inning.get('overs', []):
                over_num = over.get('over', 0)
                over_runs = sum(d.get('runs', {}).get('total', 0) for d in over.get('deliveries', []))
                total_runs += over_runs
                
                over_numbers.append(over_num)
                cumulative_runs.append(total_runs)
            
            ax.plot(over_numbers, cumulative_runs, marker='o', label=team_name, 
                   color=colors[idx], linewidth=2, markersize=4)
        
        ax.set_xlabel('Overs', fontsize=12, color='#cbd5e1')
        ax.set_ylabel('Runs', fontsize=12, color='#cbd5e1')
        ax.set_title('Worm Chart - Cumulative Runs', fontsize=14, color='#38bdf8', fontweight='bold')
        ax.legend(facecolor='#1e293b', edgecolor='#475569', fontsize=10, labelcolor='#e2e8f0')
        ax.grid(True, alpha=0.2, color='#475569')
        ax.tick_params(colors='#cbd5e1')
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating worm chart: {str(e)}")
        return None


def create_manhattan_chart(match_data, team_number):
    """Create manhattan chart manually"""
    try:
        innings = match_data.get('innings', [])
        if team_number > len(innings):
            return None
        
        target_inning = innings[team_number - 1]
        team_name = target_inning.get('team', f'Team {team_number}')
        
        over_runs = []
        over_numbers = []
        
        for over in target_inning.get('overs', []):
            over_num = over.get('over', 0)
            runs = sum(d.get('runs', {}).get('total', 0) for d in over.get('deliveries', []))
            over_numbers.append(over_num + 1)
            over_runs.append(runs)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('#1e293b')
        ax.set_facecolor('#0f172a')
        
        bars = ax.bar(over_numbers, over_runs, color='#22d3ee', edgecolor='#38bdf8', linewidth=1.5)
        
        # Highlight high-scoring overs
        max_runs = max(over_runs) if over_runs else 0
        for i, (bar, runs) in enumerate(zip(bars, over_runs)):
            if runs >= 15:
                bar.set_color('#10b981')
            elif runs >= 10:
                bar.set_color('#38bdf8')
        
        ax.set_xlabel('Over Number', fontsize=12, color='#cbd5e1')
        ax.set_ylabel('Runs Scored', fontsize=12, color='#cbd5e1')
        ax.set_title(f'Manhattan Chart - {team_name}', fontsize=14, color='#38bdf8', fontweight='bold')
        ax.grid(True, alpha=0.2, axis='y', color='#475569')
        ax.tick_params(colors='#cbd5e1')
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating manhattan chart: {str(e)}")
        return None


def render_analysis_page(match_id: str):
    """Render the match analysis interface"""
    
    service = MatchService()
    
    # Get match info
    match_summary = service.get_match_summary(match_id)
    team1 = match_summary.get('team1', 'Team1')
    team2 = match_summary.get('team2', 'Team2')
    
    # Display header with bright, clear styling
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%); padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h1 style='color: #ffffff; font-size: 2.5rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>📊 Match Analysis</h1>
        <h2 style='color: #f0f9ff; font-size: 2rem; margin: 0.5rem 0 0 0;'>{team1} vs {team2}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Match details in colored box
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;'>
        <p style='color: #ffffff; font-size: 1.1rem; margin: 0;'>
            <strong>📅 {match_summary.get('match_date', 'N/A')}</strong> | 
            <strong>🏟️ {match_summary.get('venue', 'N/A')}</strong> |
            <strong>🏆 Winner: {match_summary.get('winner', 'N/A')}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Load match JSON
    match_data = service.load_match_json(match_id)
    
    if not match_data:
        st.error("❌ Could not load match data")
        if st.button("⬅️ Back to Search", type="secondary"):
            st.session_state['view_mode'] = 'search'
            st.rerun()
        return
    
    # Create tabs for different analysis categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Match Info", 
        "🏏 Scorecards", 
        "📊 Visualizations",
        "📈 Statistics"
    ])
    
    # TAB 1: Match Info
    with tab1:
        st.markdown("### 📄 Complete Match Information")
        
        if st.button("📥 View Match Info", use_container_width=True, type="primary", key="match_info_btn"):
            info = match_data.get('info', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Match Details")
                st.write(f"**Teams:** {', '.join(info.get('teams', []))}")
                st.write(f"**Venue:** {info.get('venue', 'N/A')}")
                st.write(f"**City:** {info.get('city', 'N/A')}")
                st.write(f"**Date:** {', '.join(info.get('dates', []))}")
                st.write(f"**Match Type:** {info.get('match_type', 'N/A')}")
                st.write(f"**Gender:** {info.get('gender', 'N/A')}")
                st.write(f"**Overs:** {info.get('overs', 'N/A')}")
            
            with col2:
                st.markdown("#### Match Result")
                toss = info.get('toss', {})
                st.write(f"**Toss Winner:** {toss.get('winner', 'N/A')}")
                st.write(f"**Toss Decision:** {toss.get('decision', 'N/A')}")
                
                outcome = info.get('outcome', {})
                st.write(f"**Winner:** {outcome.get('winner', 'N/A')}")
                st.write(f"**Result:** {outcome.get('result', 'N/A')}")
                
                player_of_match = info.get('player_of_match', [])
                if player_of_match:
                    st.write(f"**Player of Match:** {', '.join(player_of_match)}")
            
            # Download option
            json_str = json.dumps(info, indent=2)
            st.download_button(
                "💾 Download Match Info (JSON)",
                data=json_str,
                file_name=f"{match_id}_match_info.json",
                mime="application/json",
                use_container_width=True
            )
    
    # TAB 2: Scorecards
    with tab2:
        st.markdown("### 🏏 Full Scorecards")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### {team1}")
            
            if st.button(f"📊 View Scorecard", use_container_width=True, type="primary", key="scorecard1"):
                scorecard = create_manual_scorecard(match_data, 1)
                
                if scorecard:
                    st.markdown("**Batting Performance**")
                    st.dataframe(scorecard['batting'], use_container_width=True, hide_index=True)
                    
                    st.markdown("**Bowling Performance**")
                    st.dataframe(scorecard['bowling'], use_container_width=True, hide_index=True)
                    
                    # Download
                    csv_data = scorecard['batting'].to_csv(index=False) + "\n\nBowling:\n" + scorecard['bowling'].to_csv(index=False)
                    st.download_button(
                        "💾 Download Scorecard (CSV)",
                        data=csv_data,
                        file_name=f"{match_id}_{team1}_scorecard.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            if st.button("📈 View Extras", use_container_width=True, key="extras1"):
                extras = create_manual_extras(match_data, 1)
                if extras is not None:
                    st.dataframe(extras, use_container_width=True)
                    
                    csv_data = extras.to_csv(index=False)
                    st.download_button(
                        "💾 Download Extras (CSV)",
                        data=csv_data,
                        file_name=f"{match_id}_{team1}_extras.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            if st.button("🎯 Fall of Wickets", use_container_width=True, key="fow1"):
                fow = create_manual_fall_of_wickets(match_data, 1)
                if fow is not None:
                    st.dataframe(fow, use_container_width=True, hide_index=True)
                    
                    csv_data = fow.to_csv(index=False)
                    st.download_button(
                        "💾 Download FOW (CSV)",
                        data=csv_data,
                        file_name=f"{match_id}_{team1}_fow.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        with col2:
            st.markdown(f"#### {team2}")
            
            if st.button(f"📊 View Scorecard", use_container_width=True, type="primary", key="scorecard2"):
                scorecard = create_manual_scorecard(match_data, 2)
                
                if scorecard:
                    st.markdown("**Batting Performance**")
                    st.dataframe(scorecard['batting'], use_container_width=True, hide_index=True)
                    
                    st.markdown("**Bowling Performance**")
                    st.dataframe(scorecard['bowling'], use_container_width=True, hide_index=True)
                    
                    csv_data = scorecard['batting'].to_csv(index=False) + "\n\nBowling:\n" + scorecard['bowling'].to_csv(index=False)
                    st.download_button(
                        "💾 Download Scorecard (CSV)",
                        data=csv_data,
                        file_name=f"{match_id}_{team2}_scorecard.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            if st.button("📈 View Extras", use_container_width=True, key="extras2"):
                extras = create_manual_extras(match_data, 2)
                if extras is not None:
                    st.dataframe(extras, use_container_width=True)
                    
                    csv_data = extras.to_csv(index=False)
                    st.download_button(
                        "💾 Download Extras (CSV)",
                        data=csv_data,
                        file_name=f"{match_id}_{team2}_extras.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            if st.button("🎯 Fall of Wickets", use_container_width=True, key="fow2"):
                fow = create_manual_fall_of_wickets(match_data, 2)
                if fow is not None:
                    st.dataframe(fow, use_container_width=True, hide_index=True)
                    
                    csv_data = fow.to_csv(index=False)
                    st.download_button(
                        "💾 Download FOW (CSV)",
                        data=csv_data,
                        file_name=f"{match_id}_{team2}_fow.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    
    # TAB 3: Visualizations
    with tab3:
        st.markdown("### 📊 Match Visualizations")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("#### 🐛 Worm Chart")
            st.caption("Cumulative runs progression for both teams")
            
            if st.button("Generate Worm Chart", use_container_width=True, type="primary", key="worm_btn"):
                with st.spinner("Creating worm chart..."):
                    fig = create_worm_chart(match_data)
                    
                    if fig:
                        st.pyplot(fig)
                        
                        # Save option
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='#1e293b')
                        buf.seek(0)
                        
                        st.download_button(
                            "💾 Download Chart (PNG)",
                            data=buf,
                            file_name=f"{match_id}_worm_chart.png",
                            mime="image/png",
                            use_container_width=True
                        )
                        plt.close(fig)
        
        with viz_col2:
            st.markdown("#### 🏙️ Manhattan Chart")
            st.caption("Runs scored in each over")
            
            team_selection = st.radio(
                "Select Team:",
                options=[f"Team 1: {team1}", f"Team 2: {team2}"],
                key="manhattan_team_radio"
            )
            
            team_num = 1 if "Team 1" in team_selection else 2
            
            if st.button("Generate Manhattan Chart", use_container_width=True, type="primary", key="manhattan_btn"):
                with st.spinner("Creating manhattan chart..."):
                    fig = create_manhattan_chart(match_data, team_num)
                    
                    if fig:
                        st.pyplot(fig)
                        
                        # Save option
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='#1e293b')
                        buf.seek(0)
                        
                        team_name = team1 if team_num == 1 else team2
                        st.download_button(
                            "💾 Download Chart (PNG)",
                            data=buf,
                            file_name=f"{match_id}_manhattan_{team_name}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                        plt.close(fig)
    
    # TAB 4: Statistics
    with tab4:
        st.markdown("### 📈 Advanced Match Statistics")
        
        df = service.convert_to_ball_by_ball_csv(match_id)
        
        if df is not None and not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏏 Top Batters")
                
                top_scorers = df.groupby('batter').agg({
                    'runs_off_bat': 'sum',
                    'ball': 'count'
                }).rename(columns={'runs_off_bat': 'Runs', 'ball': 'Balls'})
                
                top_scorers['Strike Rate'] = (top_scorers['Runs'] / top_scorers['Balls'] * 100).round(2)
                top_scorers = top_scorers.sort_values('Runs', ascending=False).head(10)
                
                st.dataframe(top_scorers, use_container_width=True)
            
            with col2:
                st.markdown("#### ⚾ Top Bowlers")
                
                wickets = df[df['is_wicket'] == 1].groupby('bowler')['is_wicket'].sum()
                runs_conceded = df.groupby('bowler')['total_runs'].sum()
                
                bowler_stats = pd.DataFrame({
                    'Wickets': wickets,
                    'Runs': runs_conceded
                }).fillna(0)
                
                bowler_stats = bowler_stats.sort_values('Wickets', ascending=False).head(10)
                
                st.dataframe(bowler_stats, use_container_width=True)
    
    # Back button
    st.markdown("---")
    if st.button("⬅️ Back to Search Results", type="secondary", use_container_width=False):
        st.session_state['view_mode'] = 'search'
        st.rerun()