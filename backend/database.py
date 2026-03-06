"""
Database module for storing and querying match metadata
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
from backend.config import DB_PATH


class MatchDatabase:
    """Handles all database operations for match metadata"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                folder_name TEXT NOT NULL,
                match_type TEXT NOT NULL,
                tournament TEXT,
                season TEXT,
                gender TEXT,
                team1 TEXT NOT NULL,
                team2 TEXT NOT NULL,
                match_date TEXT,
                venue TEXT,
                city TEXT,
                toss_winner TEXT,
                toss_decision TEXT,
                winner TEXT,
                result TEXT,
                player_of_match TEXT,
                umpires TEXT,
                match_format TEXT,
                overs INTEGER,
                is_franchise BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_type ON matches(match_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tournament ON matches(tournament)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_season ON matches(season)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_gender ON matches(gender)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_team1 ON matches(team1)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_team2 ON matches(team2)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_date ON matches(match_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venue ON matches(venue)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_franchise ON matches(is_franchise)')
        
        conn.commit()
        conn.close()
    
    def insert_match(self, match_data: Dict) -> bool:
        """Insert a match record into the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO matches (
                    match_id, file_path, folder_name, match_type, tournament, season,
                    gender, team1, team2, match_date, venue, city, toss_winner,
                    toss_decision, winner, result, player_of_match, umpires,
                    match_format, overs, is_franchise
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_data.get('match_id'),
                match_data.get('file_path'),
                match_data.get('folder_name'),
                match_data.get('match_type'),
                match_data.get('tournament'),
                match_data.get('season'),
                match_data.get('gender'),
                match_data.get('team1'),
                match_data.get('team2'),
                match_data.get('match_date'),
                match_data.get('venue'),
                match_data.get('city'),
                match_data.get('toss_winner'),
                match_data.get('toss_decision'),
                match_data.get('winner'),
                match_data.get('result'),
                match_data.get('player_of_match'),
                match_data.get('umpires'),
                match_data.get('match_format'),
                match_data.get('overs'),
                match_data.get('is_franchise', 0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting match: {e}")
            return False
    
    def search_matches(self, filters: Dict) -> List[Dict]:
        """Search matches based on comprehensive filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query dynamically based on filters
        query = "SELECT * FROM matches WHERE 1=1"
        params = []
        
        # Match type filter
        if filters.get('match_type'):
            query += " AND match_type = ?"
            params.append(filters['match_type'])
        
        # Tournament filter (for franchise leagues)
        if filters.get('tournament'):
            query += " AND tournament = ?"
            params.append(filters['tournament'])
        
        # Season filter
        if filters.get('season'):
            query += " AND season = ?"
            params.append(filters['season'])
        
        # Franchise league filter
        if filters.get('is_franchise') is not None:
            query += " AND is_franchise = ?"
            params.append(1 if filters['is_franchise'] else 0)
        
        # Gender filter
        if filters.get('gender'):
            query += " AND gender = ?"
            params.append(filters['gender'])
        
        # Team filter (either team1 or team2)
        if filters.get('teams') and len(filters['teams']) > 0:
            team_conditions = []
            for team in filters['teams']:
                team_conditions.append("(team1 = ? OR team2 = ?)")
                params.extend([team, team])
            query += f" AND ({' OR '.join(team_conditions)})"
        
        # Opposition filter (one team is selected team, other is opposition)
        if filters.get('opposition'):
            if filters.get('teams') and len(filters['teams']) > 0:
                # If teams are selected, opposition should be against them
                opp = filters['opposition']
                selected_teams = filters['teams']
                opp_conditions = []
                for team in selected_teams:
                    opp_conditions.append("((team1 = ? AND team2 = ?) OR (team1 = ? AND team2 = ?))")
                    params.extend([team, opp, opp, team])
                query += f" AND ({' OR '.join(opp_conditions)})"
            else:
                # If no teams selected, just filter for matches involving opposition
                query += " AND (team1 = ? OR team2 = ?)"
                params.extend([filters['opposition'], filters['opposition']])
        
        # Year filter (specific years)
        if filters.get('selected_years') and len(filters['selected_years']) > 0:
            year_conditions = []
            for year in filters['selected_years']:
                year_conditions.append("match_date LIKE ?")
                params.append(f"{year}%")
            query += f" AND ({' OR '.join(year_conditions)})"
        
        # Date range filter (only if years not selected)
        elif not filters.get('selected_years'):
            if filters.get('start_date'):
                query += " AND match_date >= ?"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND match_date <= ?"
                params.append(filters['end_date'])
        
        # Venue filter
        if filters.get('venue'):
            query += " AND venue = ?"
            params.append(filters['venue'])
        
        # City/Host country filter
        if filters.get('city'):
            query += " AND city = ?"
            params.append(filters['city'])
        
        # Venue type filter (Home/Away/Neutral)
        if filters.get('venue_type') and filters.get('teams') and len(filters['teams']) > 0:
            venue_type = filters['venue_type']
            selected_teams = filters['teams']
            
            if venue_type == 'Home':
                # Match is at team's home (city matches team's country)
                # This is simplified - in reality would need more data
                home_conditions = []
                for team in selected_teams:
                    home_conditions.append("(team1 = ? OR team2 = ?)")
                    params.extend([team, team])
                query += f" AND ({' OR '.join(home_conditions)})"
            
            elif venue_type == 'Neutral':
                # For now, we'll mark neutral based on venue name containing "neutral" or specific criteria
                query += " AND (venue LIKE ? OR city NOT IN (SELECT DISTINCT city FROM matches WHERE team1 = ? OR team2 = ?))"
                params.append("%neutral%")
                if selected_teams:
                    params.extend([selected_teams[0], selected_teams[0]])
        
        # Toss filter
        if filters.get('toss_filter') and filters.get('toss_team'):
            toss_team = filters['toss_team']
            toss_result = filters['toss_filter']
            
            if toss_result == 'Won':
                query += " AND toss_winner = ?"
                params.append(toss_team)
            elif toss_result == 'Lost':
                query += " AND toss_winner != ? AND toss_winner IS NOT NULL"
                params.append(toss_team)
        
        # Result filter
        if filters.get('result_filter'):
            result = filters['result_filter']
            
            if result == 'Tied':
                query += " AND result LIKE ?"
                params.append("%tie%")
            elif result == 'No Result':
                query += " AND (result LIKE ? OR winner IS NULL)"
                params.append("%no result%")
            elif result in ['Won', 'Lost'] and filters.get('result_team'):
                result_team = filters['result_team']
                if result == 'Won':
                    query += " AND winner = ?"
                    params.append(result_team)
                elif result == 'Lost':
                    query += " AND winner != ? AND winner IS NOT NULL AND (team1 = ? OR team2 = ?)"
                    params.extend([result_team, result_team, result_team])
        
        # Player search
        if filters.get('player_name'):
            # This requires JSON parsing which is slow, but we'll do a simple match for now
            query += " AND player_of_match LIKE ?"
            params.append(f"%{filters['player_name']}%")
        
        # Order by date descending
        query += " ORDER BY match_date DESC"
        
        # Pagination
        if filters.get('limit'):
            query += " LIMIT ?"
            params.append(filters['limit'])
        
        if filters.get('offset'):
            query += " OFFSET ?"
            params.append(filters['offset'])
        
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            matches = []
            for row in rows:
                matches.append(dict(row))
            
            conn.close()
            return matches
        except Exception as e:
            print(f"Search error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            conn.close()
            return []
    
    def get_match_by_id(self, match_id: str) -> Optional[Dict]:
        """Get a specific match by match_id"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_teams(self) -> List[str]:
        """Get all unique teams from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT team1 FROM matches
            UNION
            SELECT DISTINCT team2 FROM matches
            ORDER BY team1
        """)
        
        teams = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return teams
    
    def get_all_venues(self) -> List[str]:
        """Get all unique venues from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT venue FROM matches WHERE venue IS NOT NULL ORDER BY venue")
        venues = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return venues
    
    def get_all_cities(self) -> List[str]:
        """Get all unique cities from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT city FROM matches WHERE city IS NOT NULL ORDER BY city")
        cities = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return cities
    
    def get_all_tournaments(self) -> List[str]:
        """Get all unique tournaments from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT tournament FROM matches WHERE tournament IS NOT NULL ORDER BY tournament")
        tournaments = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tournaments
    
    def get_all_seasons(self) -> List[str]:
        """Get all unique seasons from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT season FROM matches WHERE season IS NOT NULL ORDER BY season DESC")
        seasons = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return seasons
    
    def get_franchise_leagues(self) -> List[str]:
        """Get all franchise league types"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT match_type FROM matches 
            WHERE is_franchise = 1 
            ORDER BY match_type
        """)
        leagues = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return leagues
    
    def get_match_count(self) -> int:
        """Get total number of matches in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM matches")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def clear_database(self):
        """Clear all records from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM matches")
        conn.commit()
        conn.close()