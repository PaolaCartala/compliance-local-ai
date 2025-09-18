"""
Database initialization script for Baker Compliant AI.

This script creates the SQLite database and initializes it with the schema.
This is the shared database initialization used by all services.
"""

import sqlite3
import sys
from pathlib import Path

def get_database_path() -> Path:
    """Get the shared database path."""
    # Database is always in the database/ directory at project root
    project_root = Path(__file__).parent.parent
    return project_root / "database" / "baker_compliant_ai.db"

def get_schema_path() -> Path:
    """Get the schema file path."""
    return Path(__file__).parent / "schema.sql"

def initialize_database():
    """Initialize the database with the schema."""
    try:
        # Get paths
        schema_path = get_schema_path()
        db_path = get_database_path()
        
        # Create database directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read schema
        if not schema_path.exists():
            print(f"❌ Error: Schema file not found at {schema_path}")
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Create database
        print(f"📁 Creating shared database at: {db_path.absolute()}")
        
        conn = sqlite3.connect(str(db_path))
        conn.executescript(schema)
        conn.commit()
        
        # Verify tables were created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ Shared database created successfully!")
        print(f"📊 Tables created: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_mock_users():
    """Create mock users for development and testing."""
    try:
        db_path = get_database_path()
        
        if not db_path.exists():
            print("❌ Error: Database does not exist. Run initialize_database() first.")
            return False
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            print(f"ℹ️  Users already exist ({user_count} users found)")
            conn.close()
            return True
        
        # Insert mock users
        mock_users = [
            ("user_001", "user1@baker.com", "Financial Advisor 1", "financial_advisor"),
            ("user_002", "user2@baker.com", "Compliance Officer 1", "compliance_officer"),
            ("user_003", "user3@baker.com", "Administrator 1", "administrator"),
        ]
        
        for azure_id, email, display_name, role in mock_users:
            cursor.execute("""
                INSERT INTO users (azure_user_id, email, display_name, role)
                VALUES (?, ?, ?, ?)
            """, (azure_id, email, display_name, role))
        
        conn.commit()
        print(f"✅ Created {len(mock_users)} mock users")
        
        # Verify users were created
        cursor.execute("SELECT email, display_name, role FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"   - {user[1]} ({user[0]}) - {user[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating mock users: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Baker Compliant AI - Shared Database Initialization")
    print("=" * 60)
    
    # Initialize database
    if initialize_database():
        # Create mock users
        create_mock_users()
        print("\n✅ Database setup completed successfully!")
        print(f"📁 Database location: {get_database_path().absolute()}")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)