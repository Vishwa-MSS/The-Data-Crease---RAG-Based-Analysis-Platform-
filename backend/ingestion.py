"""
Data ingestion module - scans JSON files and extracts metadata
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from backend.config import DATA_DIR, DATA_FOLDERS
from backend.database import MatchDatabase


class DataIngestion:
    """Handles scanning and indexing of cricket match JSON files"""
    
    def __init__(self):
        self.db = MatchDatabase()
        self.data_dir = DATA_DIR
    
    def extract_metadata(self, json_file_path: Path, folder_name: str) -> Optional[Dict]:
        """
        Extract metadata from a single JSON file
        IMPROVED VERSION - More robust extraction, handles all edge cases
        Returns a dictionary with match metadata or None if error
        """
        try:
            # Read JSON with proper error handling
            with open(json_file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON decode error in {json_file_path.name}: {e}")
                    return None
            
            # Validate basic structure
            if not isinstance(data, dict):
                print(f"⚠️  Invalid data structure in {json_file_path.name}")
                return None
            
            # Extract match info
            info = data.get('info', {})
            
            if not info:
                print(f"⚠️  No info section in {json_file_path.name}")
                return None
            
            # Get match ID - try multiple sources
            match_id = None
            if 'match_id' in info:
                match_id = str(info['match_id'])
            elif 'id' in info:
                match_id = str(info['id'])
            else:
                # Use file name as fallback
                match_id = json_file_path.stem
            
            # Extract teams - handle various formats
            teams = info.get('teams', [])
            if not teams or len(teams) < 2:
                # Try alternative location
                teams = info.get('team', [])
            
            if len(teams) >= 2:
                team1 = str(teams[0])
                team2 = str(teams[1])
            elif len(teams) == 1:
                team1 = str(teams[0])
                team2 = "Unknown"
            else:
                team1 = "Unknown"
                team2 = "Unknown"
            
            # Extract dates - handle multiple formats
            dates = info.get('dates', [])
            if not dates:
                dates = info.get('date', [])
            
            if dates and len(dates) > 0:
                match_date = str(dates[0])
            else:
                match_date = None
            
            # Extract gender - handle variations
            gender_raw = info.get('gender', 'male')
            if not gender_raw:
                gender_raw = 'male'
            
            gender = 'Male' if str(gender_raw).lower() == 'male' else 'Female'
            
            # Extract venue information - be flexible
            venue_info = info.get('venue', '')
            if not venue_info:
                venue_info = info.get('ground', '')
            
            city_info = info.get('city', '')
            if not city_info:
                city_info = info.get('location', '')
            
            # Extract toss information
            toss_info = info.get('toss', {})
            toss_winner = str(toss_info.get('winner', '')) if toss_info else ''
            toss_decision = str(toss_info.get('decision', '')) if toss_info else ''
            
            # Extract outcome - handle different formats
            outcome = info.get('outcome', {})
            if not outcome:
                outcome = {}
            
            winner = str(outcome.get('winner', ''))
            if not winner:
                winner = str(outcome.get('team', ''))
            
            # Result description
            result = ''
            if 'by' in outcome:
                by_info = outcome['by']
                if 'runs' in by_info:
                    result = f"by {by_info['runs']} runs"
                elif 'wickets' in by_info:
                    result = f"by {by_info['wickets']} wickets"
            
            if not result:
                result = str(outcome.get('result', ''))
            
            # Player of the match
            player_of_match_list = info.get('player_of_match', [])
            if not player_of_match_list:
                player_of_match_list = info.get('pom', [])
            
            if player_of_match_list:
                if isinstance(player_of_match_list, list):
                    player_of_match = str(player_of_match_list[0])
                else:
                    player_of_match = str(player_of_match_list)
            else:
                player_of_match = ''
            
            # Umpires
            officials = info.get('officials', {})
            umpires_list = officials.get('umpires', [])
            if umpires_list:
                umpires = ', '.join([str(u) for u in umpires_list])
            else:
                umpires = ''
            
            # Match format and overs
            match_type_value = info.get('match_type', '')
            overs = info.get('overs', 0)
            
            # Try to get from other fields if not present
            if not overs:
                overs = info.get('balls_per_over', 6) * info.get('overs_per_innings', 0)
            
            # Determine match format with better logic
            match_format = ''
            if match_type_value:
                match_format = str(match_type_value)
            elif overs == 20 or folder_name in ['T20_Internationals', 'Non_Official_T20']:
                match_format = "T20"
            elif overs == 50 or folder_name == 'One_Day_Internationals':
                match_format = "ODI"
            elif folder_name == 'tests_json' or folder_name == 'Multiday_Matches':
                match_format = "Test"
            else:
                match_format = DATA_FOLDERS.get(folder_name, folder_name)
            
            # Extract tournament/event information
            event_info = info.get('event', {})
            tournament = ''
            season = ''
            
            if isinstance(event_info, dict):
                tournament = str(event_info.get('name', ''))
                # Try to extract season/year from tournament name or match number
                match_number_str = str(event_info.get('match_number', ''))
                if match_number_str:
                    season = match_number_str
            elif isinstance(event_info, str):
                tournament = event_info
            
            # If no tournament from event, try to get from other fields
            if not tournament:
                tournament = str(info.get('tournament', ''))
            if not tournament:
                tournament = str(info.get('competition', ''))
            
            # Try to extract season from dates or season field
            if not season:
                season = str(info.get('season', ''))
            
            # If still no season, try to extract year from date
            if not season and match_date:
                try:
                    year = match_date.split('-')[0]
                    season = year
                except:
                    season = ''
            
            # Determine if this is a franchise league
            franchise_leagues = ['ipl_json', 'bpl_json', 'hundred_json', 'cpl_json', 
                               'sa20_json', 'psl_json', 'bbl_json', 'lpl_json']
            is_franchise = 1 if folder_name in franchise_leagues else 0
            
            # If franchise but no tournament set, use folder type
            if is_franchise and not tournament:
                tournament = DATA_FOLDERS.get(folder_name, '')
            
            metadata = {
                'match_id': match_id,
                'file_path': str(json_file_path),
                'folder_name': folder_name,
                'match_type': DATA_FOLDERS.get(folder_name, folder_name),
                'tournament': tournament,
                'season': season,
                'is_franchise': is_franchise,
                'gender': gender,
                'team1': team1,
                'team2': team2,
                'match_date': match_date,
                'venue': venue_info,
                'city': city_info,
                'toss_winner': toss_winner,
                'toss_decision': toss_decision,
                'winner': winner,
                'result': result,
                'player_of_match': player_of_match,
                'umpires': umpires,
                'match_format': match_format,
                'overs': int(overs) if overs else 0
            }
            
            return metadata
            
        except FileNotFoundError:
            print(f"⚠️  File not found: {json_file_path}")
            return None
        except Exception as e:
            print(f"⚠️  Error processing {json_file_path.name}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scan_folder(self, folder_path: Path, folder_name: str) -> int:
        """
        Scan a single folder for JSON files and extract metadata
        Returns the number of files processed
        """
        count = 0
        json_files = list(folder_path.glob('*.json'))
        
        total_files = len(json_files)
        print(f"Scanning {folder_name}: {total_files} files found")
        
        for idx, json_file in enumerate(json_files, 1):
            if idx % 100 == 0:
                print(f"  Processing {idx}/{total_files}...")
            
            metadata = self.extract_metadata(json_file, folder_name)
            if metadata:
                self.db.insert_match(metadata)
                count += 1
        
        return count
    
    def scan_all_folders(self, force_refresh: bool = False) -> Dict[str, int]:
        """
        Scan all data folders and build the metadata database
        Returns a dictionary with folder names and file counts
        
        Args:
            force_refresh: If True, clears existing database before scanning
        """
        if force_refresh:
            print("Clearing existing database...")
            self.db.clear_database()
        
        results = {}
        total_processed = 0
        
        print(f"Starting data ingestion from {self.data_dir}")
        print("-" * 60)
        
        for folder_name in DATA_FOLDERS.keys():
            folder_path = self.data_dir / folder_name
            
            if not folder_path.exists():
                print(f"⚠️  Folder not found: {folder_name}")
                results[folder_name] = 0
                continue
            
            count = self.scan_folder(folder_path, folder_name)
            results[folder_name] = count
            total_processed += count
            print(f"✓ {folder_name}: {count} matches indexed")
        
        print("-" * 60)
        print(f"Total matches indexed: {total_processed}")
        
        return results
    
    def get_ingestion_status(self) -> Dict:
        """Get the current status of data ingestion"""
        total_matches = self.db.get_match_count()
        
        status = {
            'total_matches': total_matches,
            'database_exists': self.db.db_path.exists(),
            'data_directory_exists': self.data_dir.exists()
        }
        
        # Check which folders exist
        for folder_name in DATA_FOLDERS.keys():
            folder_path = self.data_dir / folder_name
            status[f'folder_{folder_name}'] = folder_path.exists()
        
        return status


def run_ingestion(force_refresh: bool = False):
    """
    Convenience function to run data ingestion
    Can be called from command line or Streamlit
    """
    ingestion = DataIngestion()
    results = ingestion.scan_all_folders(force_refresh=force_refresh)
    return results


if __name__ == "__main__":
    # Run ingestion when called directly
    print("=" * 60)
    print("Cricket Match Data Ingestion")
    print("=" * 60)
    results = run_ingestion(force_refresh=True)