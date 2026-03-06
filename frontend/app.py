"""
Cricket Match Explorer - Main Application
Professional cricket analytics platform with RAG and cricsummary integration
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import MatchDatabase
from backend.ingestion import DataIngestion
from frontend.styles import get_custom_css
from frontend.components import (
    render_filters,
    display_filter_summary,
    render_match_table,
    render_match_cards,
    render_ball_by_ball_data,
    render_match_info,
    render_analysis_page
)


# Page configuration
st.set_page_config(
    page_title="Cricket Match Explorer",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'view_mode' not in st.session_state:
        st.session_state['view_mode'] = 'search'
    
    if 'selected_match_id' not in st.session_state:
        st.session_state['selected_match_id'] = None
    
    if 'data_ingested' not in st.session_state:
        st.session_state['data_ingested'] = False
    
    if 'current_filters' not in st.session_state:
        st.session_state['current_filters'] = {}
    
    if 'search_results' not in st.session_state:
        st.session_state['search_results'] = []


def check_data_status():
    """Check if data has been ingested"""
    db = MatchDatabase()
    count = db.get_match_count()
    return count > 0


def show_landing_page():
    """Display landing page"""
    
    st.markdown("""
    # 🏏 Cricket Match Explorer
    ### Professional Cricket Analytics Platform
    """)
    
    st.markdown("""
    Welcome to the **Cricket Match Explorer** - your comprehensive tool for exploring and analyzing cricket matches 
    from multiple formats and tournaments.
    
    #### 🎯 Features:
    - 🔍 **Advanced Search & Filtering** - Find matches by team, date, format, and more
    - 📊 **Ball-by-Ball Analysis** - Detailed delivery-level data for every match
    - 📈 **Visual Analytics** - Worm charts, Manhattan charts, and advanced statistics
    - 💾 **Data Export** - Download analysis in CSV and image formats
    - 🏆 **Multi-Format Support** - Tests, ODIs, T20Is, and more
    
    #### 📚 Powered by:
    - **Cricsheet Data** - Comprehensive ball-by-ball match data
    - **cricsummary Library** - Advanced cricket analytics
    - **RAG Technology** - Smart match search and retrieval
    """)
    
    st.markdown("---")
    
    # Check data status
    data_exists = check_data_status()
    
    if data_exists:
        db = MatchDatabase()
        match_count = db.get_match_count()
        
        st.success(f"✅ **Database Ready!** {match_count} matches indexed and ready to explore")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("🚀 Start Exploring Matches", use_container_width=True, type="primary"):
                st.session_state['view_mode'] = 'search'
                st.rerun()
        
        with col2:
            if st.button("🔄 Re-index Data", use_container_width=True):
                with st.spinner("Re-indexing data... This may take a few minutes."):
                    ingestion = DataIngestion()
                    results = ingestion.scan_all_folders(force_refresh=True)
                    st.success("✅ Data re-indexed successfully!")
                    st.rerun()
        
        with col3:
            if st.button("📊 Stats", use_container_width=True):
                st.session_state['view_mode'] = 'stats'
                st.rerun()
    
    else:
        st.warning("⚠️ **No data found in database**")
        
        st.info("""
        **To get started:**
        1. Place your cricket match JSON files in the `data/` folder
        2. Organize them in the following folders:
           - `Multiday_Matches/`
           - `Non_Official_T20/`
           - `One_Day_Internationals/`
           - `One_Days/`
           - `T20_Internationals/`
           - `tests_json/`
        3. Click the button below to index the data
        """)
        
        if st.button("📥 Index Data Now", use_container_width=True, type="primary"):
            with st.spinner("Indexing data... This may take several minutes depending on the number of files."):
                try:
                    ingestion = DataIngestion()
                    results = ingestion.scan_all_folders(force_refresh=True)
                    
                    total = sum(results.values())
                    
                    if total > 0:
                        st.success(f"✅ Successfully indexed {total} matches!")
                        st.session_state['data_ingested'] = True
                        
                        # Show breakdown
                        with st.expander("📋 Indexing Details"):
                            for folder, count in results.items():
                                st.write(f"**{folder}**: {count} matches")
                        
                        st.rerun()
                    else:
                        st.error("❌ No match files found. Please check your data folder.")
                
                except Exception as e:
                    st.error(f"❌ Error during indexing: {str(e)}")


def show_search_page():
    """Display search and filter page"""
    
    # Render filters in sidebar
    filters, apply_button = render_filters()
    
    # Main content
    st.markdown("# 🔍 Search Cricket Matches")
    
    # Display active filters
    display_filter_summary(filters)
    
    st.markdown("---")
    
    # Search logic
    if apply_button or len(st.session_state.get('search_results', [])) > 0:
        
        if apply_button:
            # Perform search
            with st.spinner("Searching matches..."):
                db = MatchDatabase()
                results = db.search_matches(filters)
                st.session_state['search_results'] = results
                st.session_state['current_filters'] = filters
        
        else:
            # Use cached results
            results = st.session_state['search_results']
        
        # Display results
        if results:
            # View mode selector
            view_mode = st.radio(
                "Display Mode:",
                options=["Table View", "Card View"],
                horizontal=True,
                key="display_mode"
            )
            
            st.markdown("---")
            
            if view_mode == "Table View":
                render_match_table(results)
            else:
                render_match_cards(results)
        
        else:
            st.warning("⚠️ No matches found with the selected filters.")
    
    else:
        st.info("👈 Use the filters in the sidebar and click **Apply Filters** to search for matches")
        
        # Show some stats
        db = MatchDatabase()
        total_matches = db.get_match_count()
        all_teams = db.get_all_teams()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total Matches", total_matches)
        
        with col2:
            st.metric("🏏 Unique Teams", len(all_teams))
        
        with col3:
            st.metric("🏟️ Unique Venues", len(db.get_all_venues()))


def show_stats_page():
    """Display database statistics"""
    
    st.markdown("# 📊 Database Statistics")
    
    db = MatchDatabase()
    
    # Overall stats
    st.subheader("Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_matches = db.get_match_count()
        st.metric("Total Matches", total_matches)
    
    with col2:
        all_teams = db.get_all_teams()
        st.metric("Unique Teams", len(all_teams))
    
    with col3:
        all_venues = db.get_all_venues()
        st.metric("Unique Venues", len(all_venues))
    
    with col4:
        st.metric("Formats", len(set([m['match_type'] for m in db.search_matches({})])))
    
    st.markdown("---")
    
    # Teams list
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏏 All Teams")
        if all_teams:
            for team in all_teams[:20]:  # Show first 20
                st.write(f"• {team}")
            if len(all_teams) > 20:
                st.caption(f"... and {len(all_teams) - 20} more")
    
    with col2:
        st.subheader("🏟️ Top Venues")
        if all_venues:
            for venue in all_venues[:20]:  # Show first 20
                st.write(f"• {venue}")
            if len(all_venues) > 20:
                st.caption(f"... and {len(all_venues) - 20} more")
    
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", type="secondary"):
        st.session_state['view_mode'] = 'search'
        st.rerun()


def main():
    """Main application logic"""
    
    # Initialize session state
    initialize_session_state()
    
    # Route to appropriate page based on view mode
    view_mode = st.session_state.get('view_mode', 'landing')
    
    if view_mode == 'landing' or (view_mode == 'search' and not check_data_status()):
        show_landing_page()
    
    elif view_mode == 'search':
        show_search_page()
    
    elif view_mode == 'ball_by_ball':
        match_id = st.session_state.get('selected_match_id')
        if match_id:
            render_ball_by_ball_data(match_id)
        else:
            st.error("No match selected")
            st.session_state['view_mode'] = 'search'
            st.rerun()
    
    elif view_mode == 'analysis':
        match_id = st.session_state.get('selected_match_id')
        if match_id:
            render_analysis_page(match_id)
        else:
            st.error("No match selected")
            st.session_state['view_mode'] = 'search'
            st.rerun()
    
    elif view_mode == 'info':
        match_id = st.session_state.get('selected_match_id')
        if match_id:
            render_match_info(match_id)
        else:
            st.error("No match selected")
            st.session_state['view_mode'] = 'search'
            st.rerun()
    
    elif view_mode == 'stats':
        show_stats_page()
    
    else:
        show_landing_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 2rem 0;'>
        <p>🏏 Cricket Match Explorer | Powered by Cricsheet & cricsummary</p>
        <p style='font-size: 0.85rem;'>Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()