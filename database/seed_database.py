#!/usr/bin/env python3
"""
Baker Compliant AI - Database Seeding Script

Seeds the database with consistent mock data from the frontend:
- Users from AuthContext.tsx
- Custom GPTs from mockChatData.ts
- Creates test data for complete integration testing
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def get_database_path() -> str:
    """Get the path to the shared database."""
    return str(Path(__file__).parent / "database" / "baker_compliant_ai.db")


# Frontend mock users from AuthContext.tsx
FRONTEND_USERS = [
    {
        "id": "1",
        "azure_user_id": "auth0|sarah.johnson",
        "email": "sarah.johnson@wealthfirm.com",
        "display_name": "Sarah Johnson",
        "role": "financial_advisor"
    },
    {
        "id": "2", 
        "azure_user_id": "auth0|jennifer.walsh",
        "email": "jennifer.walsh@wealthfirm.com",
        "display_name": "Jennifer Walsh",
        "role": "compliance_officer"
    },
    {
        "id": "3",
        "azure_user_id": "auth0|michael.chen",
        "email": "michael.chen@wealthfirm.com", 
        "display_name": "Michael Chen",
        "role": "administrator"
    }
]

# Frontend Custom GPTs from mockChatData.ts
FRONTEND_CUSTOM_GPTS = [
    {
        "id": "gpt_crm_001",
        "name": "CRM Assistant",
        "description": "Specialized in client relationship management and Redtail CRM integration",
        "system_prompt": "You are a specialized CRM assistant for financial advisors. You help manage client relationships, track communications, and ensure proper documentation for SEC compliance. Always prioritize client confidentiality and regulatory requirements.",
        "specialization": "crm",
        "color": "blue",
        "icon": "Users",
        "mcp_tools_enabled": {
            "redtailCRM": True,
            "albridgePortfolio": False,
            "blackDiamond": False
        },
        "user_id": "1"  # Sarah Johnson
    },
    {
        "id": "gpt_portfolio_001",
        "name": "Portfolio Analyzer", 
        "description": "Investment analysis and portfolio management with Albridge integration",
        "system_prompt": "You are a specialized portfolio analysis assistant for wealth management. You analyze investment portfolios, provide performance insights, and make SEC-compliant investment recommendations based on client risk tolerance and objectives.",
        "specialization": "portfolio",
        "color": "green",
        "icon": "TrendingUp",
        "mcp_tools_enabled": {
            "redtailCRM": False,
            "albridgePortfolio": True,
            "blackDiamond": False
        },
        "user_id": "1"  # Sarah Johnson
    },
    {
        "id": "gpt_compliance_001",
        "name": "Compliance Monitor",
        "description": "SEC compliance oversight and regulatory guidance",
        "system_prompt": "You are a specialized compliance assistant for financial advisory firms. You ensure all communications, recommendations, and documentation meet SEC and FINRA requirements. You flag potential compliance issues and provide regulatory guidance.",
        "specialization": "compliance", 
        "color": "red",
        "icon": "Shield",
        "mcp_tools_enabled": {
            "redtailCRM": True,
            "albridgePortfolio": True,
            "blackDiamond": False
        },
        "user_id": "2"  # Jennifer Walsh (CCO)
    }
]


def seed_users(cursor: sqlite3.Cursor) -> None:
    """Seed users from frontend AuthContext."""
    print("\n🔍 Seeding users from frontend AuthContext...")
    
    # Check existing users
    cursor.execute("SELECT id, email, display_name FROM users")
    existing_users = cursor.fetchall()
    
    if existing_users:
        print(f"📋 Found {len(existing_users)} existing users:")
        for user in existing_users:
            print(f"   - {user[0]}: {user[2]} ({user[1]})")
        
        response = input("\n❓ Do you want to replace existing users? (y/N): ")
        if response.lower() != 'y':
            print("⏭️  Skipping user seeding...")
            return
        
        # Delete existing users
        cursor.execute("DELETE FROM users")
        print("🗑️  Existing users deleted")
    
    # Insert frontend users
    for user in FRONTEND_USERS:
        cursor.execute("""
            INSERT INTO users (id, azure_user_id, email, display_name, role, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            user["id"],
            user["azure_user_id"],
            user["email"], 
            user["display_name"],
            user["role"],
            True
        ))
        print(f"✅ Created user: {user['display_name']} (ID: {user['id']})")


def seed_custom_gpts(cursor: sqlite3.Cursor) -> None:
    """Seed Custom GPTs from frontend mockChatData."""
    print("\n🔍 Seeding Custom GPTs from frontend mockChatData...")
    
    # Check existing custom GPTs
    cursor.execute("SELECT id, name, user_id FROM custom_gpts")
    existing_gpts = cursor.fetchall()
    
    if existing_gpts:
        print(f"📋 Found {len(existing_gpts)} existing Custom GPTs:")
        for gpt in existing_gpts:
            print(f"   - {gpt[0]}: {gpt[1]} (User: {gpt[2]})")
        
        response = input("\n❓ Do you want to replace existing Custom GPTs? (y/N): ")
        if response.lower() != 'y':
            print("⏭️  Skipping Custom GPT seeding...")
            return
        
        # Delete existing custom GPTs
        cursor.execute("DELETE FROM custom_gpts")
        print("🗑️  Existing Custom GPTs deleted")
    
    # Insert frontend Custom GPTs
    for gpt in FRONTEND_CUSTOM_GPTS:
        cursor.execute("""
            INSERT INTO custom_gpts (
                id, name, description, system_prompt, specialization, 
                color, icon, mcp_tools_enabled, is_active, user_id, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            gpt["id"],
            gpt["name"],
            gpt["description"], 
            gpt["system_prompt"],
            gpt["specialization"],
            gpt["color"],
            gpt["icon"],
            json.dumps(gpt["mcp_tools_enabled"]),
            True,
            gpt["user_id"]
        ))
        print(f"✅ Created Custom GPT: {gpt['name']} (ID: {gpt['id']}) for User {gpt['user_id']}")


def main():
    """Main seeding function."""
    print("🚀 Baker Compliant AI - Database Seeding")
    print("=" * 60)
    
    db_path = get_database_path()
    print(f"📁 Database: {db_path}")
    
    if not Path(db_path).exists():
        print("❌ Database not found! Please run 'python database/init_database.py' first.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Seed users
            seed_users(cursor)
            
            # Seed Custom GPTs  
            seed_custom_gpts(cursor)
            
            conn.commit()
            
        print("\n" + "=" * 60)
        print("🎉 DATABASE SEEDING COMPLETED!")
        print("=" * 60)
        
        # Show final state
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM custom_gpts") 
            gpt_count = cursor.fetchone()[0]
            
            print(f"📊 Final database state:")
            print(f"   - Users: {user_count}")
            print(f"   - Custom GPTs: {gpt_count}")
            
            # Show User-GPT mapping
            cursor.execute("""
                SELECT u.display_name, c.name, c.id 
                FROM users u 
                JOIN custom_gpts c ON u.id = c.user_id 
                ORDER BY u.display_name, c.name
            """)
            mappings = cursor.fetchall()
            
            if mappings:
                print(f"\n🔗 User-GPT Mappings:")
                for user_name, gpt_name, gpt_id in mappings:
                    print(f"   - {user_name}: {gpt_name} ({gpt_id})")
                    
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise


if __name__ == "__main__":
    main()