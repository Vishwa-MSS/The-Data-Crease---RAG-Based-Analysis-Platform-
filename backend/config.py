"""
Configuration settings for Cricket Explorer
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"
EXPORTS_DIR = BASE_DIR / "exports"
DB_PATH = BASE_DIR / "cricket_matches.db"

# Create directories if they don't exist
CACHE_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# Data folder structure - INCLUDING FRANCHISE LEAGUES
DATA_FOLDERS = {
    # International Cricket
    "tests_json": "Test",
    "One_Day_Internationals": "ODI",
    "T20_Internationals": "T20I",
    "Multiday_Matches": "Multiday",
    "One_Days": "One Day",
    "Non_Official_T20": "Non-Official T20",
    
    # Franchise Leagues
    "ipl_json": "IPL",  # Indian Premier League
    "bpl_json": "BPL",  # Bangladesh Premier League
    "hundred_json": "The Hundred",  # The Hundred
    "cpl_json": "CPL",  # Caribbean Premier League
    "sa20_json": "SA20",  # SA20
    "smat_json": "SMAT",  # Syed Mushtaq Ali Trophy
    "psl_json": "PSL",  # Pakistan Super League
    "bbl_json": "BBL",  # Big Bash League
    "lpl_json": "LPL"   # Lanka Premier League
}

# Gender options
GENDER_OPTIONS = ["All", "Male", "Female"]

# Match result options
RESULT_OPTIONS = ["All", "Won", "Lost", "Tied", "No Result"]

# Tournament Categories for better filtering
TOURNAMENT_CATEGORIES = {
    "International": ["Test", "ODI", "T20I"],
    "Franchise Leagues": ["IPL", "BBL", "CPL", "PSL", "BPL", "LPL", "SA20", "The Hundred"],
    "Domestic": ["Multiday", "One Day", "Non-Official T20", "SMAT"],
    "All": list(DATA_FOLDERS.values())
}

# Franchise Teams Mapping (for better filtering)
FRANCHISE_TEAMS = {
    "IPL": [
        "Chennai Super Kings", "Mumbai Indians", "Royal Challengers Bangalore",
        "Kolkata Knight Riders", "Delhi Capitals", "Punjab Kings",
        "Rajasthan Royals", "Sunrisers Hyderabad", "Gujarat Titans",
        "Lucknow Super Giants", "Rising Pune Supergiant", "Gujarat Lions",
        "Kochi Tuskers Kerala", "Pune Warriors", "Deccan Chargers"
    ],
    "BBL": [
        "Sydney Thunder", "Sydney Sixers", "Melbourne Stars", "Melbourne Renegades",
        "Perth Scorchers", "Adelaide Strikers", "Brisbane Heat", "Hobart Hurricanes"
    ],
    "CPL": [
        "Barbados Tridents", "Guyana Amazon Warriors", "Jamaica Tallawahs",
        "St Kitts and Nevis Patriots", "St Lucia Kings", "Trinbago Knight Riders",
        "Antigua Hawksbills", "Barbados Royals"
    ],
    "PSL": [
        "Islamabad United", "Karachi Kings", "Lahore Qalandars",
        "Multan Sultans", "Peshawar Zalmi", "Quetta Gladiators"
    ],
    "BPL": [
        "Dhaka Dynamites", "Chittagong Vikings", "Comilla Victorians",
        "Khulna Titans", "Rajshahi Kings", "Rangpur Riders", "Sylhet Sixers"
    ],
    "SA20": [
        "Durban Super Giants", "Joburg Super Kings", "MI Cape Town",
        "Paarl Royals", "Pretoria Capitals", "Sunrisers Eastern Cape"
    ],
    "The Hundred": [
        "Birmingham Phoenix", "London Spirit", "Manchester Originals",
        "Northern Superchargers", "Oval Invincibles", "Southern Brave",
        "Trent Rockets", "Welsh Fire"
    ]
}