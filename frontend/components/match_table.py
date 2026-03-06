"""
Match table component - displays search results
"""
import streamlit as st
import pandas as pd
from typing import List, Dict


def render_match_table(matches: List[Dict]):
    """
    Render matches in a clean, interactive table
    Returns the selected match_id if user clicks a match
    """
    
    if not matches:
        st.warning("⚠️ No matches found with the selected filters. Try adjusting your criteria.")
        return None
    
    st.success(f"✅ Found **{len(matches)}** match(es)")
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(matches)
    
    # Select and order columns for display
    display_columns = ['match_id', 'team1', 'team2', 'match_date', 'venue', 'match_type', 'gender', 'winner']
    
    # Only include columns that exist
    available_columns = [col for col in display_columns if col in df.columns]
    df_display = df[available_columns].copy()
    
    # Rename columns for better readability
    column_mapping = {
        'match_id': 'Match ID',
        'team1': 'Team 1',
        'team2': 'Team 2',
        'match_date': 'Date',
        'venue': 'Venue',
        'match_type': 'Format',
        'gender': 'Gender',
        'winner': 'Winner'
    }
    
    df_display = df_display.rename(columns=column_mapping)
    
    # Format date if present
    if 'Date' in df_display.columns:
        df_display['Date'] = pd.to_datetime(df_display['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Display the table with row selection
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Create a selection interface
    st.markdown("---")
    st.subheader("📊 Select a Match to View Details")
    
    # Create match labels for selection
    match_labels = []
    match_id_map = {}
    
    for match in matches:
        label = f"{match['team1']} vs {match['team2']} - {match['match_date']} ({match['match_type']})"
        match_labels.append(label)
        match_id_map[label] = match['match_id']
    
    selected_label = st.selectbox(
        "Choose a match:",
        options=match_labels,
        key="match_selection"
    )
    
    if selected_label:
        selected_match_id = match_id_map[selected_label]
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("🏏 View Ball-by-Ball Data", use_container_width=True, type="primary"):
                st.session_state['selected_match_id'] = selected_match_id
                st.session_state['view_mode'] = 'ball_by_ball'
                st.rerun()
        
        with col2:
            if st.button("📊 View Match Analysis", use_container_width=True, type="primary"):
                st.session_state['selected_match_id'] = selected_match_id
                st.session_state['view_mode'] = 'analysis'
                st.rerun()
        
        with col3:
            if st.button("ℹ️ Match Info", use_container_width=True):
                st.session_state['selected_match_id'] = selected_match_id
                st.session_state['view_mode'] = 'info'
                st.rerun()
    
    return None


def render_match_cards(matches: List[Dict]):
    """
    Alternative view: Render matches as cards (more visual)
    """
    
    if not matches:
        st.warning("⚠️ No matches found")
        return None
    
    st.success(f"✅ Found **{len(matches)}** match(es)")
    
    # Display matches in a grid
    cols_per_row = 2
    
    for i in range(0, len(matches), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(matches):
                match = matches[i + j]
                
                with col:
                    with st.container():
                        st.markdown(f"""
                        <div class="match-card">
                            <h3 style="color: #38bdf8; margin-bottom: 0.5rem;">
                                {match['team1']} vs {match['team2']}
                            </h3>
                            <p style="color: #94a3b8; margin: 0.25rem 0;">
                                📅 {match['match_date']} | 🏟️ {match.get('venue', 'Unknown')}
                            </p>
                            <p style="color: #cbd5e1; margin: 0.25rem 0;">
                                <span class="cricket-badge">{match['match_type']}</span>
                                <span class="cricket-badge">{match['gender']}</span>
                            </p>
                            {f"<p style='color: #10b981; margin: 0.5rem 0;'>🏆 Winner: {match['winner']}</p>" if match.get('winner') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Action buttons
                        btn_col1, btn_col2 = st.columns(2)
                        
                        with btn_col1:
                            if st.button("🏏 Ball Data", key=f"ball_{match['match_id']}", use_container_width=True):
                                st.session_state['selected_match_id'] = match['match_id']
                                st.session_state['view_mode'] = 'ball_by_ball'
                                st.rerun()
                        
                        with btn_col2:
                            if st.button("📊 Analysis", key=f"analysis_{match['match_id']}", use_container_width=True):
                                st.session_state['selected_match_id'] = match['match_id']
                                st.session_state['view_mode'] = 'analysis'
                                st.rerun()