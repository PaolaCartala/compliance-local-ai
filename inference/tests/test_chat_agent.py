#!/usr/bin/env python3
"""
Temporary test script for ChatAgent with conservative Ollama settings.
Tests the agent with a simple question to verify stability.
"""

import asyncio
import json
from datetime import datetime, UTC
from typing import Dict, Any

from inference.src.agents.chat_agent import ChatAgent
from inference.src.utils.logging import logger


async def test_chat_agent():
    """Test the ChatAgent with a simple financial question."""
    
    # Initialize the chat agent
    chat_agent = ChatAgent()
    
    try:
        # Initialize with Ollama configuration
        await chat_agent.initialize(
            base_url="http://localhost:11434/v1",
            chat_model="gpt-oss:latest",
            vision_model="llama3.2-vision:11b"
        )
        
        logger.info("ChatAgent initialized successfully")
        
        # Simulate complex financial advisor input for high-capacity testing
        test_input = {
            "message_id": "test_msg_001",
            "thread_id": "test_thread_001", 
            "custom_gpt_config": {
                "id": "portfolio_advisor",  # Use portfolio specialization for comprehensive testing
                "user_id": "test_user_001", 
                "name": "Portfolio Analysis Specialist",
                "specialization": "portfolio",
                "system_prompt": "You are an expert portfolio analyst with deep knowledge of modern portfolio theory, risk management, and SEC compliance.",
                "temperature": 0.3,
                "max_tokens": 2048  # Increased for comprehensive responses
            },
            "user_message": """I have a client with a $2.5M portfolio currently allocated as follows: 60% large-cap US equities, 25% bonds (mix of corporate and government), 10% international developed markets, and 5% REITs. 

The client is 45 years old, has a moderate-aggressive risk tolerance, and wants to optimize for long-term growth while maintaining some downside protection. They're concerned about inflation and recent market volatility.

Please provide a comprehensive analysis of their current allocation and recommendations for optimization, including specific asset class suggestions, risk assessment, and any compliance considerations I should be aware of when making these recommendations.""",
            "conversation_history": [],
            "attachments": []
        }
        
        logger.info("Starting chat processing with test input", 
                   message_id=test_input["message_id"],
                   user_message=test_input["user_message"])
        
        # Process the chat message with correct parameters
        start_time = datetime.now(UTC)
        
        response = await chat_agent.process_chat(
            message_id=test_input["message_id"],
            thread_id=test_input["thread_id"],
            custom_gpt=test_input["custom_gpt_config"],  # Pass the config directly
            user_message=test_input["user_message"],
            context_messages=test_input["conversation_history"],
            attachments=test_input["attachments"]
        )
        
        end_time = datetime.now(UTC)
        total_time = int((end_time - start_time).total_seconds() * 1000)
        
        # Display results
        print("\n" + "="*60)
        print("CHAT AGENT TEST RESULTS")
        print("="*60)
        print(f"Input Question: {test_input['user_message']}")
        print(f"Processing Time: {total_time}ms")
        print("-"*60)
        print("RESPONSE:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print("="*60)
        
        # Log success
        if "error" not in response:
            logger.info("Chat agent test completed successfully",
                       processing_time_ms=total_time,
                       response_length=len(response.get("content", "")),
                       confidence_score=response.get("confidence_score", 0))
            print("✅ Test PASSED - Agent responded successfully")
        else:
            logger.warning("Chat agent test completed with error",
                          error=response.get("error"),
                          processing_time_ms=total_time)
            print("⚠️  Test completed with ERROR")
            
    except Exception as e:
        logger.error("Chat agent test failed", error=str(e), exc_info=True)
        print(f"\n❌ Test FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    print("Starting ChatAgent Test with Conservative Ollama Settings...")
    print("Testing simple question: 'What is inflation?'")
    print("-" * 60)
    
    # Run the test
    asyncio.run(test_chat_agent())