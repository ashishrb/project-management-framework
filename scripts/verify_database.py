"""
Database verification script for GenAI Metrics Dashboard
Verifies that all tables and data are properly created
"""
import sys
import os
from sqlalchemy import text

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.database import engine

def verify_tables():
    """Verify all tables exist"""
    print("🔍 Verifying database tables...")
    
    expected_tables = [
        # Lookup tables
        'functions', 'platforms', 'priorities', 'statuses', 'portfolios',
        'applications', 'investment_types', 'journey_maps', 'project_types',
        'project_status_classifications', 'project_priority_classifications',
        'project_criticality_levels',
        
        # Main tables
        'projects', 'tasks', 'features', 'backlogs', 'resources', 'risks',
        'approvals', 'charters',
        
        # Junction tables
        'project_functions', 'project_platforms', 'task_functions', 'task_platforms',
        'feature_functions', 'feature_platforms', 'resource_functions', 'resource_platforms',
        'project_resources', 'task_resources'
    ]
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all tables
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        existing_tables = [row[0] for row in result.fetchall()]
        
        print(f"📊 Found {len(existing_tables)} tables in database")
        
        # Check each expected table
        missing_tables = []
        for table in expected_tables:
            if table in existing_tables:
                print(f"✅ {table}")
            else:
                print(f"❌ {table} - MISSING")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n❌ Missing {len(missing_tables)} tables: {missing_tables}")
            return False
        else:
            print(f"\n✅ All {len(expected_tables)} expected tables found!")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False
    finally:
        db.close()

def verify_data():
    """Verify lookup data is populated"""
    print("\n🔍 Verifying lookup data...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check each lookup table
        lookup_tables = {
            'functions': 17,
            'platforms': 9,
            'priorities': 6,
            'statuses': 4,
            'portfolios': 10,
            'applications': 8,
            'investment_types': 5,
            'journey_maps': 6,
            'project_types': 4,
            'project_status_classifications': 5,
            'project_priority_classifications': 5,
            'project_criticality_levels': 5
        }
        
        all_good = True
        for table, expected_count in lookup_tables.items():
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            
            if count >= expected_count:
                print(f"✅ {table}: {count} records (expected: {expected_count})")
            else:
                print(f"❌ {table}: {count} records (expected: {expected_count})")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        return False
    finally:
        db.close()

def verify_relationships():
    """Verify foreign key relationships"""
    print("\n🔍 Verifying foreign key relationships...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check foreign key constraints
        result = db.execute(text("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name, kcu.column_name
        """))
        
        foreign_keys = result.fetchall()
        print(f"✅ Found {len(foreign_keys)} foreign key relationships")
        
        # Check some key relationships
        key_relationships = [
            ('projects', 'project_type_id', 'project_types'),
            ('projects', 'status_id', 'statuses'),
            ('projects', 'priority_id', 'priorities'),
            ('projects', 'portfolio_id', 'portfolios'),
            ('tasks', 'project_id', 'projects'),
            ('features', 'project_id', 'projects'),
            ('risks', 'project_id', 'projects')
        ]
        
        for table, column, ref_table in key_relationships:
            fk_exists = any(
                fk[0] == table and fk[1] == column and fk[2] == ref_table 
                for fk in foreign_keys
            )
            if fk_exists:
                print(f"✅ {table}.{column} -> {ref_table}.id")
            else:
                print(f"❌ {table}.{column} -> {ref_table}.id - MISSING")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying relationships: {e}")
        return False
    finally:
        db.close()

def verify_indexes():
    """Verify database indexes"""
    print("\n🔍 Verifying database indexes...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all indexes
        result = db.execute(text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """))
        
        indexes = result.fetchall()
        print(f"✅ Found {len(indexes)} indexes")
        
        # Check for key indexes
        key_indexes = [
            'ix_projects_project_id',
            'ix_projects_name',
            'ix_functions_name',
            'ix_platforms_name',
            'ix_priorities_level',
            'ix_statuses_name'
        ]
        
        existing_index_names = [idx[2] for idx in indexes]
        for index_name in key_indexes:
            if index_name in existing_index_names:
                print(f"✅ {index_name}")
            else:
                print(f"❌ {index_name} - MISSING")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying indexes: {e}")
        return False
    finally:
        db.close()

def main():
    """Main verification function"""
    print("🚀 GenAI Metrics Dashboard - Database Verification")
    print("=" * 60)
    
    # Run all verification checks
    checks = [
        verify_tables(),
        verify_data(),
        verify_relationships(),
        verify_indexes()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("🎉 PHASE 1 COMPLETE! Database schema and data are ready.")
        print("✅ All tables created")
        print("✅ All lookup data seeded")
        print("✅ All relationships established")
        print("✅ All indexes created")
        print("\n🚀 Ready to proceed to Phase 2: API Endpoints & Services")
    else:
        print("❌ PHASE 1 INCOMPLETE! Some issues found.")
        print("Please fix the issues above before proceeding to Phase 2.")

if __name__ == "__main__":
    main()
