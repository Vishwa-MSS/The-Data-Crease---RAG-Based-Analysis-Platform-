"""
Match detail component - displays ball-by-ball data and match info
"""
import streamlit as st
import pandas as pd
from backend.match_service import MatchService
from datetime import datetime


def render_match_info(match_id: str):
    """Display detailed match information"""
    
    service = MatchService()
    match_summary = service.get_match_summary(match_id)
    
    if not match_summary:
        st.error("❌ Could not load match information")
        return
    
    # Display match header
    st.markdown(f"""
    # 🏏 {match_summary['team1']} vs {match_summary['team2']}
    """)
    
    # Match metadata in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Date", match_summary.get('match_date', 'N/A'))
    
    with col2:
        st.metric("🏟️ Venue", match_summary.get('venue', 'N/A'))
    
    with col3:
        st.metric("🎯 Format", match_summary.get('match_type', 'N/A'))
    
    with col4:
        st.metric("👥 Gender", match_summary.get('gender', 'N/A'))
    
    st.markdown("---")
    
    # Additional details in expandable sections
    with st.expander("📋 Match Details", expanded=True):
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown(f"""
            **Match ID:** {match_summary.get('match_id', 'N/A')}  
            **City:** {match_summary.get('city', 'N/A')}  
            **Season:** {match_summary.get('season', 'N/A')}  
            **Event:** {match_summary.get('event_name', 'N/A')}  
            """)
        
        with detail_col2:
            st.markdown(f"""
            **Toss Winner:** {match_summary.get('toss_winner', 'N/A')}  
            **Toss Decision:** {match_summary.get('toss_decision', 'N/A')}  
            **Winner:** {match_summary.get('winner', 'N/A')}  
            **Player of Match:** {match_summary.get('player_of_match', 'N/A')}  
            """)
    
    # Umpires info
    if match_summary.get('umpires'):
        with st.expander("👨‍⚖️ Officials"):
            st.markdown(f"**Umpires:** {match_summary['umpires']}")
    
    # Back button
    st.markdown("---")
    if st.button("⬅️ Back to Search Results", type="secondary"):
        st.session_state['view_mode'] = 'search'
        st.rerun()


def render_ball_by_ball_data(match_id: str):
    """Display ball-by-ball data with download option"""
    
    service = MatchService()
    
    # Get match info first
    match_summary = service.get_match_summary(match_id)
    team1 = match_summary.get('team1', 'Team1')
    team2 = match_summary.get('team2', 'Team2')
    
    # Display header
    st.markdown(f"""
    # 🏏 Ball-by-Ball Data
    ## {team1} vs {team2}
    """)
    
    st.info(f"📅 {match_summary.get('match_date', 'N/A')} | 🏟️ {match_summary.get('venue', 'N/A')}")
    
    st.markdown("---")
    
    # Load ball-by-ball data
    with st.spinner("Loading ball-by-ball data..."):
        df = service.convert_to_ball_by_ball_csv(match_id)
    
    if df is None or df.empty:
        st.error("❌ Could not load ball-by-ball data for this match")
        if st.button("⬅️ Back to Search", type="secondary"):
            st.session_state['view_mode'] = 'search'
            st.rerun()
        return
    
    # Display summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Balls", len(df))
    
    with col2:
        total_wickets = df['is_wicket'].sum()
        st.metric("Total Wickets", int(total_wickets))
    
    with col3:
        total_runs = df['total_runs'].sum()
        st.metric("Total Runs", int(total_runs))
    
    with col4:
        total_innings = df['innings'].nunique()
        st.metric("Innings", total_innings)
    
    st.markdown("---")
    
    # Innings selector
    innings_options = sorted(df['innings'].unique())
    selected_innings = st.selectbox(
        "Select Innings to View:",
        options=['All'] + list(innings_options),
        key="innings_selector"
    )
    
    # Filter data
    if selected_innings != 'All':
        df_display = df[df['innings'] == selected_innings].copy()
        st.info(f"Showing innings {selected_innings}")
    else:
        df_display = df.copy()
    
    # Display data
    st.subheader("📊 Ball-by-Ball Details")
    
    # Add formatting
    df_display = df_display.reset_index(drop=True)
    
    # Display with custom height
    st.dataframe(
        df_display,
        use_container_width=True,
        height=500
    )
    
    st.markdown("---")
    
    # Download section
    st.subheader("💾 Download Options")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Convert to CSV for download
        csv_data = df.to_csv(index=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{match_id}_{team1}_vs_{team2}_ball_by_ball_{timestamp}.csv"
        
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        if selected_innings != 'All':
            csv_innings = df_display.to_csv(index=False)
            filename_innings = f"{match_id}_{team1}_vs_{team2}_innings{selected_innings}_{timestamp}.csv"
            
            st.download_button(
                label=f"📥 Download Innings {selected_innings} (CSV)",
                data=csv_innings,
                file_name=filename_innings,
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
    
    with col3:
        if st.button("⬅️ Back", use_container_width=True, type="secondary"):
            st.session_state['view_mode'] = 'search'
            st.rerun()
    
    # Additional insights
    with st.expander("📈 Quick Insights", expanded=False):
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.markdown("### Top Batters (Runs)")
            top_batters = df.groupby('batter')['runs_off_bat'].sum().sort_values(ascending=False).head(10)
            st.dataframe(top_batters, use_container_width=True)
        
        with insight_col2:
            st.markdown("### Top Bowlers (Wickets)")
            top_bowlers = df[df['is_wicket'] == 1].groupby('bowler')['is_wicket'].sum().sort_values(ascending=False).head(10)
            st.dataframe(top_bowlers, use_container_width=True)