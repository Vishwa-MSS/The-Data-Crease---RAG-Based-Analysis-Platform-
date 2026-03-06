"""
COMPLETE FILTER SYSTEM - Including Franchise Leagues
All filters with tournament, season, and league-specific options
"""
import streamlit as st
from datetime import datetime
from backend.database import MatchDatabase
from backend.config import DATA_FOLDERS, GENDER_OPTIONS, TOURNAMENT_CATEGORIES


def render_filters():
    """Render comprehensive filter sidebar with franchise league support"""
    
    st.sidebar.markdown("""
    <h1 style='color: #0c4a6e; font-size: 1.8rem; margin-bottom: 1rem;'>🏏 Match Filters</h1>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    db = MatchDatabase()
    
    # Get all filter options
    all_teams = ['All'] + db.get_all_teams()
    all_venues = ['All'] + db.get_all_venues()
    all_cities = ['All'] + db.get_all_cities()
    all_tournaments = ['All'] + db.get_all_tournaments()
    all_seasons = ['All'] + db.get_all_seasons()
    
    # ==================================================================
    # SECTION 1: TOURNAMENT CATEGORY (NEW!)
    # ==================================================================
    st.sidebar.markdown("### 🏆 Tournament Category")
    
    tournament_category = st.sidebar.radio(
        "Select Category:",
        options=["All Cricket", "International Only", "Franchise Leagues Only", "Domestic Only"],
        key="tournament_category",
        help="Filter by tournament type"
    )
    
    # Determine is_franchise filter based on category
    is_franchise_filter = None
    category_match_types = None
    
    if tournament_category == "Franchise Leagues Only":
        is_franchise_filter = True
    elif tournament_category == "International Only":
        category_match_types = TOURNAMENT_CATEGORIES["International"]
    elif tournament_category == "Domestic Only":
        category_match_types = TOURNAMENT_CATEGORIES["Domestic"]
    
    st.sidebar.markdown("---")
    
    # ==================================================================
    # SECTION 2: BASIC FILTERS
    # ==================================================================
    st.sidebar.markdown("### 📊 Basic Filters")
    
    # Match Type Filter with smart options based on category
    available_match_types = ["All"]
    
    if tournament_category == "Franchise Leagues Only":
        # Show only franchise leagues
        available_match_types.extend(TOURNAMENT_CATEGORIES["Franchise Leagues"])
    elif tournament_category == "International Only":
        available_match_types.extend(TOURNAMENT_CATEGORIES["International"])
    elif tournament_category == "Domestic Only":
        available_match_types.extend(TOURNAMENT_CATEGORIES["Domestic"])
    else:
        # Show all
        available_match_types.extend(list(DATA_FOLDERS.values()))
    
    selected_match_type = st.sidebar.selectbox(
        "🎯 League/Format",
        options=available_match_types,
        index=0,
        key="match_type_filter",
        help="Select specific league or format"
    )
    
    # Tournament Filter (for franchise leagues)
    if tournament_category in ["All Cricket", "Franchise Leagues Only"]:
        selected_tournament = st.sidebar.selectbox(
            "🏆 Tournament/Edition",
            options=all_tournaments,
            index=0,
            key="tournament_filter",
            help="Select specific tournament or season edition"
        )
    else:
        selected_tournament = None
    
    # Season Filter
    if all_seasons:
        selected_season = st.sidebar.selectbox(
            "📅 Season/Year",
            options=all_seasons,
            index=0,
            key="season_filter",
            help="Filter by season"
        )
    else:
        selected_season = None
    
    # Gender Filter
    selected_gender = st.sidebar.selectbox(
        "👥 Gender",
        options=GENDER_OPTIONS,
        index=0,
        key="gender_filter",
        help="Filter by gender"
    )
    
    st.sidebar.markdown("---")
    
    # ==================================================================
    # SECTION 3: TEAM FILTERS
    # ==================================================================
    st.sidebar.markdown("### 🏏 Team Selection")
    
    team_filter_type = st.sidebar.radio(
        "Team Filter:",
        options=["All Teams", "Specific Teams"],
        key="team_filter_type",
        horizontal=True
    )
    
    if team_filter_type == "Specific Teams":
        selected_teams = st.sidebar.multiselect(
            "Select Team(s)",
            options=[t for t in all_teams if t != 'All'],
            default=[],
            key="teams_filter",
            help="Select one or more teams (works for both international and franchise)"
        )
    else:
        selected_teams = []
    
    st.sidebar.markdown("---")
    
    # ==================================================================
    # SECTION 4: DATE FILTERS
    # ==================================================================
    st.sidebar.markdown("### 📅 Date Filters")
    
    date_filter_type = st.sidebar.radio(
        "Filter By:",
        options=["Date Range", "Specific Years", "All Time"],
        key="date_filter_type"
    )
    
    start_date = None
    end_date = None
    selected_years = []
    
    if date_filter_type == "Date Range":
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            start_date = st.date_input(
                "From",
                value=datetime(2020, 1, 1),
                key="start_date_filter"
            )
        
        with col2:
            end_date = st.date_input(
                "To",
                value=datetime.now(),
                key="end_date_filter"
            )
    
    elif date_filter_type == "Specific Years":
        current_year = datetime.now().year
        year_range = list(range(2000, current_year + 1))
        year_range.reverse()
        
        selected_years = st.sidebar.multiselect(
            "Select Year(s)",
            options=year_range,
            default=[],
            key="years_filter",
            help="Select one or multiple years"
        )
    
    st.sidebar.markdown("---")
    
    # ==================================================================
    # SECTION 5: ADVANCED FILTERS
    # ==================================================================
    with st.sidebar.expander("🔧 Advanced Filters", expanded=False):
        
        # Venue Filter
        st.markdown("#### 🏟️ Venue")
        selected_venue = st.selectbox(
            "Venue",
            options=all_venues,
            index=0,
            key="venue_filter"
        )
        
        # Host City Filter
        st.markdown("#### 🌍 Host City")
        selected_city = st.selectbox(
            "Host City",
            options=all_cities,
            index=0,
            key="city_filter"
        )
        
        # Opposition Filter
        st.markdown("#### 🆚 Opposition")
        opposition_filter_type = st.radio(
            "Opposition:",
            options=["All", "Specific Team"],
            key="opposition_filter_type",
            horizontal=True
        )
        
        selected_opposition = None
        if opposition_filter_type == "Specific Team":
            selected_opposition = st.selectbox(
                "Select Opposition",
                options=[t for t in all_teams if t != 'All'],
                key="opposition_filter"
            )
        
        # Toss Result Filter
        st.markdown("#### 🪙 Toss Result")
        toss_filter_type = st.radio(
            "Toss:",
            options=["All", "Won", "Lost"],
            key="toss_filter_type",
            horizontal=True
        )
        
        toss_winner_team = None
        if toss_filter_type != "All":
            toss_winner_team = st.selectbox(
                "Select Team for Toss Filter",
                options=[t for t in all_teams if t != 'All'],
                key="toss_team_filter"
            )
        
        # Match Result Filter
        st.markdown("#### 🏆 Match Result")
        result_filter = st.selectbox(
            "Result",
            options=["All", "Won", "Lost", "Tied", "No Result"],
            index=0,
            key="result_filter"
        )
        
        result_team = None
        if result_filter in ["Won", "Lost"]:
            result_team = st.selectbox(
                "Select Team for Result Filter",
                options=[t for t in all_teams if t != 'All'],
                key="result_team_filter"
            )
        
        # Player Search
        st.markdown("#### 👤 Player Search")
        player_name = st.text_input(
            "Player Name",
            value="",
            key="player_filter",
            help="Search matches involving a player"
        )
    
    st.sidebar.markdown("---")
    
    # ==================================================================
    # ACTION BUTTONS
    # ==================================================================
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        apply_filters = st.button(
            "🔍 Search", 
            use_container_width=True, 
            type="primary"
        )
    
    with col2:
        reset_filters = st.button(
            "🔄 Reset", 
            use_container_width=True
        )
    
    # Reset logic
    if reset_filters:
        for key in list(st.session_state.keys()):
            if key.endswith('_filter') or key.endswith('_filter_type') or key == 'tournament_category':
                del st.session_state[key]
        st.rerun()
    
    # ==================================================================
    # BUILD FILTERS DICTIONARY
    # ==================================================================
    filters = {
        'match_type': selected_match_type if selected_match_type != 'All' else None,
        'tournament': selected_tournament if selected_tournament and selected_tournament != 'All' else None,
        'season': selected_season if selected_season and selected_season != 'All' else None,
        'is_franchise': is_franchise_filter,
        'gender': selected_gender if selected_gender != 'All' else None,
        'teams': selected_teams if selected_teams else None,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
        'selected_years': selected_years if selected_years else None,
        'venue': selected_venue if selected_venue != 'All' else None,
        'city': selected_city if selected_city != 'All' else None,
        'opposition': selected_opposition,
        'toss_filter': toss_filter_type if toss_filter_type != 'All' else None,
        'toss_team': toss_winner_team,
        'result_filter': result_filter if result_filter != 'All' else None,
        'result_team': result_team,
        'player_name': player_name if player_name else None,
        'limit': 300,
        'offset': 0
    }
    
    return filters, apply_filters


def display_filter_summary(filters):
    """Display active filters with franchise league highlighting"""
    active_filters = []
    
    # Tournament Category
    if filters.get('is_franchise') is True:
        active_filters.append("**Category:** Franchise Leagues")
    elif filters.get('is_franchise') is False:
        active_filters.append("**Category:** International/Domestic")
    
    if filters.get('match_type'):
        active_filters.append(f"**League/Format:** {filters['match_type']}")
    
    if filters.get('tournament'):
        active_filters.append(f"**Tournament:** {filters['tournament']}")
    
    if filters.get('season'):
        active_filters.append(f"**Season:** {filters['season']}")
    
    if filters.get('gender'):
        active_filters.append(f"**Gender:** {filters['gender']}")
    
    if filters.get('teams') and len(filters['teams']) > 0:
        teams_str = ", ".join(filters['teams'])
        active_filters.append(f"**Teams:** {teams_str}")
    
    if filters.get('selected_years'):
        years_str = ", ".join(map(str, filters['selected_years']))
        active_filters.append(f"**Years:** {years_str}")
    elif filters.get('start_date') or filters.get('end_date'):
        date_range = f"{filters.get('start_date', 'any')} to {filters.get('end_date', 'any')}"
        active_filters.append(f"**Date Range:** {date_range}")
    
    if filters.get('venue'):
        active_filters.append(f"**Venue:** {filters['venue']}")
    
    if filters.get('city'):
        active_filters.append(f"**Host City:** {filters['city']}")
    
    if filters.get('opposition'):
        active_filters.append(f"**Opposition:** {filters['opposition']}")
    
    if filters.get('toss_filter') and filters.get('toss_team'):
        active_filters.append(f"**Toss:** {filters['toss_team']} {filters['toss_filter']}")
    
    if filters.get('result_filter'):
        if filters.get('result_team'):
            active_filters.append(f"**Result:** {filters['result_team']} {filters['result_filter']}")
        else:
            active_filters.append(f"**Result:** {filters['result_filter']}")
    
    if filters.get('player_name'):
        active_filters.append(f"**Player:** {filters['player_name']}")
    
    if active_filters:
        filters_html = "<br>".join([
            f"<span style='color: #ffffff; background: linear-gradient(135deg, #0ea5e9, #0284c7); padding: 0.35rem 0.85rem; border-radius: 20px; margin: 0.25rem; display: inline-block; font-weight: 600;'>{f}</span>" 
            for f in active_filters
        ])
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 2px solid #0ea5e9;'>
            <h3 style='color: #0c4a6e; margin: 0 0 1rem 0; font-size: 1.3rem; font-weight: 800;'>🎯 Active Filters</h3>
            <div>{filters_html}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 2px solid #94a3b8;'>
            <p style='color: #475569; margin: 0; font-size: 1.1rem; font-weight: 600;'>ℹ️ No filters applied - showing all available matches</p>
        </div>
        """, unsafe_allow_html=True)