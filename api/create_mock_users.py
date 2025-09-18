#!/usr/bin/env python3
"""
Create mock users for Baker Compliant AI demonstration.

[TODO] This is a temporary implementation for demonstration purposes.
Replace with Microsoft Entra ID integration in production.
"""

import sqlite3
import uuid
from datetime import datetime

def create_mock_users():
    """Create mock users based on frontend data for demonstration."""
    
    # Database path
    db_path = "api/database/baker_compliant_ai.db"
    
    # [TODO] Mock users - Replace with Entra ID integration
    mock_users = [
        {
            "id": "user-sarah-johnson",
            "azure_user_id": "auth0|sarah.johnson",  # [TODO] Replace with actual Entra ID
            "email": "sarah.johnson@bakergroup.com",
            "display_name": "Sarah Johnson, CFP",
            "role": "financial_advisor"
        },
        {
            "id": "user-michael-chen", 
            "azure_user_id": "auth0|michael.chen",  # [TODO] Replace with actual Entra ID
            "email": "michael.chen@bakergroup.com",
            "display_name": "Michael Chen, CFP",
            "role": "financial_advisor"
        },
        {
            "id": "user-lisa-wang",
            "azure_user_id": "auth0|lisa.wang",  # [TODO] Replace with actual Entra ID
            "email": "lisa.wang@bakergroup.com", 
            "display_name": "Lisa Wang, CFP",
            "role": "financial_advisor"
        },
        {
            "id": "user-david-park",
            "azure_user_id": "auth0|david.park",  # [TODO] Replace with actual Entra ID
            "email": "david.park@bakergroup.com",
            "display_name": "David Park, CFP", 
            "role": "financial_advisor"
        },
        {
            "id": "user-compliance-officer",
            "azure_user_id": "auth0|compliance.officer",  # [TODO] Replace with actual Entra ID
            "email": "compliance@bakergroup.com",
            "display_name": "Compliance Officer",
            "role": "compliance_officer"
        },
        {
            "id": "user-admin",
            "azure_user_id": "auth0|admin",  # [TODO] Replace with actual Entra ID
            "email": "admin@bakergroup.com",
            "display_name": "System Administrator", 
            "role": "administrator"
        },
        {
            "id": "test-user-123",  # Keep existing test user for backward compatibility
            "azure_user_id": "auth0|testuser",
            "email": "testuser@bakergroup.com",
            "display_name": "Test User",
            "role": "financial_advisor"
        }
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧑‍💼 Creating mock users for demonstration...")
        print("=" * 60)
        
        for user in mock_users:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (id, azure_user_id, email, display_name, role, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, TRUE, datetime('now'), datetime('now'))
                """, (
                    user["id"],
                    user["azure_user_id"], 
                    user["email"],
                    user["display_name"],
                    user["role"]
                ))
                
                print(f"✅ Created user: {user['display_name']} ({user['email']}) - {user['role']}")
                
            except sqlite3.Error as e:
                print(f"❌ Error creating user {user['email']}: {e}")
        
        conn.commit()
        
        # Verify users were created
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n📊 Total users in database: {user_count}")
        
        # Show all users
        cursor.execute("SELECT id, email, display_name, role FROM users ORDER BY role, display_name")
        users = cursor.fetchall()
        
        print("\n👥 Current users:")
        print("-" * 60)
        for user in users:
            print(f"   {user[2]} ({user[1]}) - {user[3]}")
        
        conn.close()
        
        print("\n🎉 Mock users created successfully!")
        print("\n[TODO] Integration notes:")
        print("- Replace auth0|* IDs with actual Microsoft Entra ID user IDs")
        print("- Implement proper JWT token validation with Entra ID")
        print("- Add role-based access control (RBAC) based on Entra ID groups")
        print("- Remove mock authentication in production")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    create_mock_users()