"""
Authentication utilities for Baker Compliant AI.

[TODO] MOCK IMPLEMENTATION - Replace with Microsoft Entra ID integration
This is a placeholder implementation for demonstration purposes only.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer

from api.src.utils.logging import logger

# [TODO] Replace with actual Entra ID configuration
# Placeholder security scheme
security = HTTPBearer(auto_error=False)

# [TODO] MOCK USERS - Replace with Entra ID user data
MOCK_USERS = {
    "sarah.johnson": {
        "id": "user-sarah-johnson",
        "azure_user_id": "auth0|sarah.johnson",
        "email": "sarah.johnson@bakergroup.com",
        "display_name": "Sarah Johnson, CFP",
        "role": "financial_advisor",
        "permissions": ["chat:read", "chat:write", "custom_gpts:read", "custom_gpts:write", "threads:read", "threads:write"]
    },
    "michael.chen": {
        "id": "user-michael-chen",
        "azure_user_id": "auth0|michael.chen", 
        "email": "michael.chen@bakergroup.com",
        "display_name": "Michael Chen, CFP",
        "role": "financial_advisor",
        "permissions": ["chat:read", "chat:write", "custom_gpts:read", "custom_gpts:write", "threads:read", "threads:write"]
    },
    "lisa.wang": {
        "id": "user-lisa-wang",
        "azure_user_id": "auth0|lisa.wang",
        "email": "lisa.wang@bakergroup.com",
        "display_name": "Lisa Wang, CFP", 
        "role": "financial_advisor",
        "permissions": ["chat:read", "chat:write", "custom_gpts:read", "custom_gpts:write", "threads:read", "threads:write"]
    },
    "compliance.officer": {
        "id": "user-compliance-officer",
        "azure_user_id": "auth0|compliance.officer",
        "email": "compliance@bakergroup.com",
        "display_name": "Compliance Officer",
        "role": "compliance_officer", 
        "permissions": ["chat:read", "custom_gpts:read", "threads:read", "audit:read", "compliance:write"]
    },
    "admin": {
        "id": "user-admin",
        "azure_user_id": "auth0|admin",
        "email": "admin@bakergroup.com",
        "display_name": "System Administrator",
        "role": "administrator",
        "permissions": ["*"]  # All permissions
    },
    "testuser": {  # Keep for backward compatibility
        "id": "test-user-123",
        "azure_user_id": "auth0|testuser",
        "email": "testuser@bakergroup.com", 
        "display_name": "Test User",
        "role": "financial_advisor",
        "permissions": ["chat:read", "chat:write", "custom_gpts:read", "threads:read", "threads:write"]
    }
}


async def get_current_user(token: Optional[str] = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user.
    
    [TODO] MOCK IMPLEMENTATION - Replace with Microsoft Entra ID JWT validation
    
    Production implementation should:
    1. Validate JWT token with Entra ID public keys
    2. Extract user claims from token
    3. Map Entra ID groups to application roles
    4. Cache user data for performance
    """
    
    # Debug: Log what we received
    logger.info(
        "[MOCK AUTH] get_current_user called",
        token_received=token,
        token_type=type(token).__name__ if token else "None",
        token_is_none=token is None,
        token_is_falsy=not token
    )
    
    # [TODO] Remove mock logic and implement Entra ID JWT validation
    if not token:
        # Return default test user for now
        user_key = "testuser"
        mock_user = MOCK_USERS[user_key].copy()
        
        logger.info(
            "[MOCK AUTH] No token provided, using default test user",
            user_id=mock_user["id"]
        )
        
        return mock_user
    
    try:
        # [TODO] Replace with proper JWT validation against Entra ID
        # For now, extract user from mock token
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = str(token)
            
        logger.info(
            "[MOCK AUTH] Parsing token",
            raw_token=str(token),
            token_str=token_str,
            token_type=type(token).__name__
        )
            
        # Simple mock token parsing (NOT secure - for demo only)
        if "sarah" in token_str.lower():
            user_key = "sarah.johnson"
        elif "michael" in token_str.lower():
            user_key = "michael.chen"
        elif "lisa" in token_str.lower():
            user_key = "lisa.wang"
        elif "compliance" in token_str.lower():
            user_key = "compliance.officer"
        elif "admin" in token_str.lower():
            user_key = "admin"
        else:
            user_key = "testuser"
            
        logger.info(
            "[MOCK AUTH] Token parsing result",
            token_str=token_str,
            user_key_selected=user_key,
            contains_sarah="sarah" in token_str.lower()
        )
            
        mock_user = MOCK_USERS[user_key].copy()
        
        logger.debug(
            "[MOCK AUTH] Authentication placeholder - using mock user",
            user_id=mock_user["id"],
            user_role=mock_user["role"]
        )
        
        return mock_user
        
    except Exception as e:
        logger.error(
            "[MOCK AUTH] Token validation failed", 
            error=str(e),
            exc_info=True
        )
        
        # Fall back to test user
        return MOCK_USERS["testuser"].copy()


def require_permission(permission: str):
    """
    Decorator to require specific permission.
    
    [TODO] MOCK IMPLEMENTATION - Implement proper RBAC with Entra ID groups
    
    Production implementation should:
    1. Check user's Entra ID group memberships
    2. Map groups to application permissions
    3. Cache permission checks for performance
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # [TODO] Implement proper permission checking
            # For now, always allow access for demonstration
            logger.debug(
                "[MOCK AUTH] Permission check bypassed",
                required_permission=permission
            )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def generate_mock_token(user_key: str) -> str:
    """
    Generate a mock JWT token for testing.
    
    [TODO] Remove this function in production - tokens should come from Entra ID
    """
    if user_key not in MOCK_USERS:
        user_key = "testuser"
        
    user = MOCK_USERS[user_key]
    
    # Create a simple mock token (NOT secure - for demo only)
    # [TODO] Remove - use proper JWT signing with Entra ID keys
    mock_token = f"mock-{user_key}-{datetime.utcnow().timestamp()}"
    
    return f"Bearer {mock_token}"


async def get_database_user_id(current_user: dict) -> Optional[str]:
    """
    Map auth system user to database user ID.
    
    Takes the current user from auth system and returns the corresponding
    database user ID by matching azure_user_id.
    """
    from api.src.services.database_adapter import db_adapter
    
    try:
        azure_user_id = current_user.get("azure_user_id")
        if not azure_user_id:
            logger.error("No azure_user_id found in current_user", user=current_user)
            return None
            
        db_user = await db_adapter.get_user_by_azure_id(azure_user_id)
        if not db_user:
            logger.error("No database user found for azure_user_id", azure_user_id=azure_user_id)
            return None
            
        return db_user["id"]
        
    except Exception as e:
        logger.error("Error mapping user to database ID", error=str(e), exc_info=True)
        return None