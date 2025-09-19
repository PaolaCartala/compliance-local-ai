"""
Test script to verify the inference service implementation.

This script tests the basic functionality of the inference service components
without requiring a full deployment.
"""

import asyncio
import sys
from pathlib import Path

# Add the inference source to the path
inference_src = Path(__file__).parent / "src"
sys.path.insert(0, str(inference_src))

from utils.config import InferenceSettings
from utils.logging import configure_logging, logger
from database.service import DatabaseService
from services.queue_service import QueueService
from agents.chat_agent import ChatAgent


async def test_configuration():
    """Test configuration loading."""
    print("Testing configuration loading...")
    settings = InferenceSettings()
    
    print(f"  ✓ Database path: {settings.database.path}")
    print(f"  ✓ Ollama URL: {settings.ollama.base_url}")
    print(f"  ✓ Chat model: {settings.ollama.chat_model}")
    print(f"  ✓ Poll interval: {settings.service.poll_interval_seconds}s")
    
    return settings


async def test_database_service(settings):
    """Test database service connection."""
    print("\nTesting database service...")
    
    db_service = DatabaseService(settings.database)
    await db_service.initialize()
    
    # Test basic connection
    result = await db_service.execute_query("SELECT 1 as test")
    assert result == [{"test": 1}], "Database query failed"
    print("  ✓ Database connection successful")
    
    await db_service.close()
    return True


async def test_queue_service(settings):
    """Test queue service functionality."""
    print("\nTesting queue service...")
    
    db_service = DatabaseService(settings.database)
    await db_service.initialize()
    
    queue_service = QueueService(db_service)
    
    # Test getting next request (should return None for empty queue)
    next_request = await queue_service.get_next_request()
    print(f"  ✓ Next request from empty queue: {next_request}")
    
    await db_service.close()
    return True


async def test_chat_agent_initialization(settings):
    """Test chat agent initialization."""
    print("\nTesting chat agent initialization...")
    
    try:
        chat_agent = ChatAgent(settings)
        print("  ✓ Chat agent created successfully")
        
        # Test initialization (this might fail if Ollama is not running)
        try:
            await chat_agent.initialize()
            print("  ✓ Chat agent initialized successfully")
            return True
        except Exception as e:
            print(f"  ⚠ Chat agent initialization failed (Ollama not running?): {e}")
            return False
            
    except Exception as e:
        print(f"  ✗ Chat agent creation failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("Baker Compliant AI - Inference Service Test Suite")
    print("=" * 50)
    
    try:
        # Configure logging
        configure_logging(log_level="INFO")
        
        # Test configuration
        settings = await test_configuration()
        
        # Test database service
        await test_database_service(settings)
        
        # Test queue service
        await test_queue_service(settings)
        
        # Test chat agent
        agent_ok = await test_chat_agent_initialization(settings)
        
        print("\n" + "=" * 50)
        print("Test Summary:")
        print("  ✓ Configuration: OK")
        print("  ✓ Database Service: OK")
        print("  ✓ Queue Service: OK")
        print(f"  {'✓' if agent_ok else '⚠'} Chat Agent: {'OK' if agent_ok else 'WARNING (Ollama required)'}")
        
        if agent_ok:
            print("\n🎉 All tests passed! The inference service is ready to run.")
        else:
            print("\n⚠ Basic components OK, but Ollama is required for full functionality.")
            print("   Make sure Ollama is running with the required models:")
            print(f"     - {settings.ollama.chat_model}")
            print(f"     - {settings.ollama.vision_model}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())