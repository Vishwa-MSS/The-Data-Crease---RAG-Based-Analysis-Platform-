"""
Match Service - handles match retrieval, CSV conversion, and analysis
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
from backend.config import CACHE_DIR, EXPORTS_DIR
from backend.database import MatchDatabase


class MatchService:
    """Service for handling match data operations"""
    
    def __init__(self):
        self.db = MatchDatabase()
        self.cache_dir = CACHE_DIR
        self.exports_dir = EXPORTS_DIR
    
    def load_match_json(self, match_id: str) -> Optional[Dict]:
        """Load the complete JSON data for a match"""
        match = self.db.get_match_by_id(match_id)
        
        if not match:
            return None
        
        file_path = Path(match['file_path'])
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading match JSON: {e}")
            return None
    
    def convert_to_ball_by_ball_csv(self, match_id: str) -> Optional[pd.DataFrame]:
        """
        Convert match JSON to ball-by-ball DataFrame
        Uses cache if available
        """
        # Check cache first
        cache_file = self.cache_dir / f"{match_id}_ball_by_ball.csv"
        
        if cache_file.exists():
            try:
                return pd.read_csv(cache_file)
            except Exception as e:
                print(f"Error reading cache: {e}")
        
        # Load and convert
        match_data = self.load_match_json(match_id)
        
        if not match_data:
            return None
        
        try:
            # Extract innings data
            innings = match_data.get('innings', [])
            
            all_balls = []
            
            for inning in innings:
                inning_number = inning.get('inning', 0)
                team = inning.get('team', '')
                overs = inning.get('overs', [])
                
                for over in overs:
                    over_number = over.get('over', 0)
                    deliveries = over.get('deliveries', [])
                    
                    for ball_idx, delivery in enumerate(deliveries, 1):
                        batter = delivery.get('batter', '')
                        bowler = delivery.get('bowler', '')
                        non_striker = delivery.get('non_striker', '')
                        
                        runs = delivery.get('runs', {})
                        batter_runs = runs.get('batter', 0)
                        extras_runs = runs.get('extras', 0)
                        total_runs = runs.get('total', 0)
                        
                        # Wickets
                        wickets = delivery.get('wickets', [])
                        wicket_type = ''
                        player_out = ''
                        
                        if wickets:
                            wicket_type = wickets[0].get('kind', '')
                            player_out = wickets[0].get('player_out', '')
                        
                        # Extras
                        extras = delivery.get('extras', {})
                        extra_type = list(extras.keys())[0] if extras else ''
                        extra_runs = extras.get(extra_type, 0) if extra_type else 0
                        
                        ball_data = {
                            'innings': inning_number,
                            'batting_team': team,
                            'over': over_number,
                            'ball': ball_idx,
                            'batter': batter,
                            'bowler': bowler,
                            'non_striker': non_striker,
                            'runs_off_bat': batter_runs,
                            'extras': extras_runs,
                            'total_runs': total_runs,
                            'extra_type': extra_type,
                            'wicket_type': wicket_type,
                            'player_out': player_out,
                            'is_wicket': 1 if wickets else 0
                        }
                        
                        all_balls.append(ball_data)
            
            # Create DataFrame
            df = pd.DataFrame(all_balls)
            
            # Save to cache
            df.to_csv(cache_file, index=False)
            
            return df
            
        except Exception as e:
            print(f"Error converting match to DataFrame: {e}")
            return None
    
    def get_match_summary(self, match_id: str) -> Dict:
        """Get a comprehensive summary of the match"""
        match = self.db.get_match_by_id(match_id)
        
        if not match:
            return {}
        
        match_data = self.load_match_json(match_id)
        
        if not match_data:
            return match  # Return basic metadata at least
        
        # Add additional computed information
        info = match_data.get('info', {})
        
        summary = {
            **match,
            'match_number': info.get('match_number', ''),
            'season': info.get('season', ''),
            'event_name': info.get('event', {}).get('name', ''),
            'total_innings': len(match_data.get('innings', []))
        }
        
        return summary
    
    def export_ball_by_ball(self, match_id: str, team1: str, team2: str) -> Optional[Path]:
        """
        Export ball-by-ball data to CSV in exports folder
        Returns the path to exported file
        """
        df = self.convert_to_ball_by_ball_csv(match_id)
        
        if df is None or df.empty:
            return None
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{match_id}_{team1}_vs_{team2}_ball_by_ball_{timestamp}.csv"
        export_path = self.exports_dir / filename
        
        try:
            df.to_csv(export_path, index=False)
            return export_path
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return None
    
    def get_teams_from_match(self, match_id: str) -> Tuple[str, str]:
        """Get team names from a match"""
        match = self.db.get_match_by_id(match_id)
        
        if match:
            return match.get('team1', ''), match.get('team2', '')
        
        return '', ''
    
    def get_innings_data(self, match_id: str, innings_number: int) -> Optional[pd.DataFrame]:
        """Get ball-by-ball data for a specific innings"""
        df = self.convert_to_ball_by_ball_csv(match_id)
        
        if df is None or df.empty:
            return None
        
        innings_df = df[df['innings'] == innings_number]
        return innings_df