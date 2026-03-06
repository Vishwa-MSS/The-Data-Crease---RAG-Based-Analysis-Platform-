#!/usr/bin/env python3
"""
Database Migration Script for Franchise Leagues
Adds tournament, season, and is_franchise columns to existing database
"""

import sqlite3
from pathlib import Path

def migrate_database(db_path='cricket_matches.db'):
    """
    Migrate existing database to support franchise leagues
    """
    print("=" * 70)
    print("CRICKET MATCH EXPLORER - DATABASE MIGRATION")
    print("Adding support for franchise leagues")
    print("=" * 70)
    
    if not Path(db_path).exists():
        print(f"\n❌ Database not found at: {db_path}")
        print("   No migration needed - new schema will be created automatically")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📊 Current Database Info:")
        cursor.execute("SELECT COUNT(*) FROM matches")
        count = cursor.fetchone()[0]
        print(f"   Total matches: {count}")
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(matches)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"   Existing columns: {len(existing_columns)}")
        
        # Add new columns if they don't exist
        new_columns = []
        
        if 'tournament' not in existing_columns:
            cursor.execute('ALTER TABLE matches ADD COLUMN tournament TEXT')
            new_columns.append('tournament')
            print("\n✅ Added column: tournament")
        else:
            print("\n✓  Column already exists: tournament")
        
        if 'season' not in existing_columns:
            cursor.execute('ALTER TABLE matches ADD COLUMN season TEXT')
            new_columns.append('season')
            print("✅ Added column: season")
        else:
            print("✓  Column already exists: season")
        
        if 'is_franchise' not in existing_columns:
            cursor.execute('ALTER TABLE matches ADD COLUMN is_franchise BOOLEAN DEFAULT 0')
            new_columns.append('is_franchise')
            print("✅ Added column: is_franchise")
        else:
            print("✓  Column already exists: is_franchise")
        
        # Create new indices
        print("\n📑 Creating indices...")
        
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tournament ON matches(tournament)')
            print("✅ Created index: idx_tournament")
        except:
            print("✓  Index already exists: idx_tournament")
        
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_season ON matches(season)')
            print("✅ Created index: idx_season")
        except:
            print("✓  Index already exists: idx_season")
        
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_franchise ON matches(is_franchise)')
            print("✅ Created index: idx_is_franchise")
        except:
            print("✓  Index already exists: idx_is_franchise")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ MIGRATION SUCCESSFUL!")
        print("=" * 70)
        
        if new_columns:
            print(f"\n📌 Added {len(new_columns)} new column(s): {', '.join(new_columns)}")
            print("\n⚠️  IMPORTANT NEXT STEPS:")
            print("   1. Re-index your data to populate new fields:")
            print("      python -c \"from backend.ingestion import run_ingestion; run_ingestion(force_refresh=True)\"")
            print("\n   2. This will extract tournament and season info from JSON files")
            print("   3. Franchise league flags will be set automatically")
        else:
            print("\n📌 All columns already exist - database is up to date")
            print("\n💡 If you've added new franchise league data:")
            print("   Re-run indexing to include it:")
            print("   python -c \"from backend.ingestion import run_ingestion; run_ingestion(force_refresh=True)\"")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return


def check_franchise_data():
    """Check if franchise league data is present"""
    print("\n" + "=" * 70)
    print("CHECKING FOR FRANCHISE LEAGUE DATA")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect('cricket_matches.db')
        cursor = conn.cursor()
        
        # Check for franchise matches
        cursor.execute("SELECT COUNT(*) FROM matches WHERE is_franchise = 1")
        franchise_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches WHERE is_franchise = 0")
        non_franchise_count = cursor.fetchone()[0]
        
        print(f"\n📊 Match Distribution:")
        print(f"   Franchise Leagues: {franchise_count}")
        print(f"   International/Domestic: {non_franchise_count}")
        print(f"   Total: {franchise_count + non_franchise_count}")
        
        if franchise_count > 0:
            print("\n🏆 Franchise Leagues Found:")
            cursor.execute("""
                SELECT DISTINCT match_type, COUNT(*) 
                FROM matches 
                WHERE is_franchise = 1 
                GROUP BY match_type
                ORDER BY match_type
            """)
            for league, count in cursor.fetchall():
                print(f"   - {league}: {count} matches")
        else:
            print("\n⚠️  No franchise league data found yet")
            print("   Add your franchise league JSON files to:")
            print("   - data/ipl_json/")
            print("   - data/bbl_json/")
            print("   - data/cpl_json/")
            print("   - data/psl_json/")
            print("   - data/bpl_json/")
            print("   - data/lpl_json/")
            print("   - data/sa20_json/")
            print("   - data/hundred_json/")
            print("   - data/smat_json/")
            print("\n   Then re-run indexing")
        
        conn.close()
        
    except Exception as e:
        print(f"\n⚠️  Could not check data: {e}")


if __name__ == "__main__":
    print("\n")
    
    # Run migration
    migrate_database()
    
    # Check existing data
    if Path('cricket_matches.db').exists():
        check_franchise_data()
    
    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print("\n")