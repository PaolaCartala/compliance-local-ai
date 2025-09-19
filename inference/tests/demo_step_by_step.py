#!/usr/bin/env python3
"""
Simple step-by-step chatbot flow demonstration.

This script demonstrates the correct flow:
1. Create a new thread via API
2. Get the real thread ID  
3. Send a message using that thread ID
4. Check the queue
5. Show the results

Fixed version that uses real thread IDs.
"""

import requests
import json
import time
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any

class StepByStepChatbotDemo:
    """Demonstrates chatbot flow with real thread creation."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sarah-token"  # Use sarah token for a known user
        }
        self.thread_id: Optional[str] = None
        self.message_id: Optional[str] = None
        
    def log(self, message: str, status: str = "📌"):
        """Simple logging function."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status} {message}")
    
    def step_1_check_api(self) -> bool:
        """Step 1: Verify API is running."""
        self.log("Step 1: Checking API health...", "🔍")
        
        try:
            response = requests.get(f"{self.api_base_url}/health/", timeout=5)
            if response.status_code == 200:
                health = response.json()
                status = health.get('status')
                # The new health check returns 'healthy', 'degraded', or 'unhealthy'
                if status in ['healthy', 'degraded']:
                    self.log(f"API is operational! Status: {status}", "✅")
                    self.log(f"Database: {health.get('database', {}).get('status', 'unknown')}", "🗄️")
                    return True
                else:
                    self.log(f"API health check failed: {status}", "❌")
                    return False
            else:
                self.log(f"API health check failed: {response.status_code}", "❌")
                return False
        except Exception as e:
            self.log(f"Cannot reach API: {e}", "❌")
            return False
    
    def step_2_create_thread(self) -> bool:
        """Step 2: Create a new thread and get its ID."""
        self.log("Step 2: Creating new thread...", "🔍")
        
        thread_data = {
            "title": f"Demo Chat - {datetime.now().strftime('%H:%M:%S')}",
            "custom_gpt_id": "gpt_portfolio_001"
        }
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/threads/",
                json=thread_data,
                headers=self.headers
            )
            
            self.log(f"Thread creation response: {response.status_code}", "📊")
            
            if response.status_code == 201:
                result = response.json()
                if result.get("success"):
                    self.thread_id = result["data"]["id"]
                    self.log(f"Thread created successfully! ID: {self.thread_id}", "✅")
                    self.log(f"Thread title: {result['data']['title']}", "📝")
                    return True
                else:
                    self.log(f"Thread creation failed: {result}", "❌")
                    return False
            else:
                self.log(f"Thread creation failed with status {response.status_code}", "❌")
                self.log(f"Response: {response.text}", "📄")
                return False
                
        except Exception as e:
            self.log(f"Thread creation error: {e}", "❌")
            return False
    
    def step_3_send_message(self) -> bool:
        """Step 3: Send a message to the created thread."""
        if not self.thread_id:
            self.log("No thread ID available!", "❌")
            return False
            
        self.log("Step 3: Sending message to thread...", "🔍")
        
        message_content = (
            "Hello! Can you analyze a portfolio for a client who is 55 years old "
            "and wants to retire in 10 years? They have a moderate risk tolerance."
        )
        
        # Use form data as the API expects
        form_data = {
            "content": message_content,
            "thread_id": self.thread_id,
            "custom_gpt_id": "gpt_portfolio_001"
        }
        
        # Remove JSON content-type for form submission
        headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        
        try:
            self.log(f"Sending to thread: {self.thread_id}", "📤")
            
            response = requests.post(
                f"{self.api_base_url}/api/v1/chat/messages",
                data=form_data,  # Form data, not JSON
                headers=headers
            )
            
            self.log(f"Message send response: {response.status_code}", "📊")
            
            if response.status_code == 202:  # Accepted for processing
                result = response.json()
                if result.get("success"):
                    self.message_id = result["data"]["id"]
                    self.log(f"Message sent and queued! ID: {self.message_id}", "✅")
                    self.log(f"Message content: {message_content[:50]}...", "📝")
                    return True
                else:
                    self.log(f"Message send failed: {result}", "❌")
                    return False
            else:
                self.log(f"Message send failed with status {response.status_code}", "❌")
                self.log(f"Response: {response.text}", "📄")
                return False
                
        except Exception as e:
            self.log(f"Message send error: {e}", "❌")
            return False
    
    def step_4_check_queue(self) -> Dict[str, Any]:
        """Step 4: Check if message is in the inference queue."""
        if not self.message_id:
            self.log("No message ID available!", "❌")
            return {}
            
        self.log("Step 4: Checking inference queue...", "🔍")
        
        try:
            # Use the shared database path
            conn = sqlite3.connect('database/baker_compliant_ai.db')
            cursor = conn.cursor()
            
            # Look for our message in the queue
            cursor.execute("""
                SELECT id, status, priority, created_at, message_id, input_data
                FROM inference_queue 
                WHERE message_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (self.message_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                queue_data = {
                    "queue_id": row[0],
                    "status": row[1], 
                    "priority": row[2],
                    "created_at": row[3],
                    "message_id": row[4],
                    "input_data": row[5]
                }
                
                self.log(f"Found in queue! Status: {queue_data['status']}", "✅")
                self.log(f"Queue ID: {queue_data['queue_id']}", "📝")
                self.log(f"Priority: {queue_data['priority']}", "📝")
                return queue_data
            else:
                self.log("Message not found in queue", "⚠️")
                return {}
                
        except Exception as e:
            self.log(f"Queue check error: {e}", "❌")
            return {}
    
    def step_5_check_messages(self) -> list:
        """Step 5: Check messages in the thread."""
        if not self.thread_id:
            self.log("No thread ID available!", "❌")
            return []
            
        self.log("Step 5: Checking thread messages...", "🔍")
        
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/chat/messages/{self.thread_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                messages = result.get("items", [])
                self.log(f"Found {len(messages)} messages in thread", "✅")
                
                for i, msg in enumerate(messages):
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")[:50]
                    msg_id = msg.get("id", "")
                    
                    self.log(f"  Message {i+1}: [{role}] {content}... (ID: {msg_id})", "📝")
                
                return messages
            else:
                self.log(f"Failed to get messages: {response.status_code}", "❌")
                return []
                
        except Exception as e:
            self.log(f"Message check error: {e}", "❌")
            return []
    
    def display_summary(self, queue_data: Dict[str, Any], messages: list):
        """Display a summary of the demonstration."""
        self.log("=== DEMONSTRATION SUMMARY ===", "📋")
        
        print(f"""
🎯 CHATBOT FLOW DEMONSTRATION RESULTS:

📊 Thread Information:
   - Thread ID: {self.thread_id}
   - Created successfully: ✅

💬 Message Information:  
   - Message ID: {self.message_id}
   - Sent successfully: ✅
   - Message count in thread: {len(messages)}

🔄 Queue Information:
   - Found in queue: {'✅' if queue_data else '❌'}
   - Queue status: {queue_data.get('status', 'Not found')}
   - Queue priority: {queue_data.get('priority', 'N/A')}

📱 Frontend Experience:
   - Thread creation: ✅ Working
   - Message sending: ✅ Working  
   - Message queuing: {'✅' if queue_data else '❌'} {'Working' if queue_data else 'Needs debugging'}
   - Message retrieval: ✅ Working

🏗️ Architecture Flow:
   Frontend → API → Database (Threads) ✅
   Frontend → API → Database (Messages) ✅
   API → SQLite Queue → (Waiting for Inference Service)

⚡ Next Steps:
   1. Start the inference service to process queued messages
   2. Test the complete end-to-end flow with AI responses
   3. Verify compliance and audit logging
        """)
    
    def run_demonstration(self):
        """Run the complete step-by-step demonstration."""
        print("🚀 Baker Compliant AI - Step-by-Step Chatbot Demo")
        print("=" * 60)
        
        # Step 1: Check API
        if not self.step_1_check_api():
            self.log("Demo aborted: API not available", "❌")
            return False
        
        # Step 2: Create thread
        if not self.step_2_create_thread():
            self.log("Demo aborted: Could not create thread", "❌")
            return False
        
        # Step 3: Send message
        if not self.step_3_send_message():
            self.log("Demo aborted: Could not send message", "❌")
            return False
        
        # Step 4: Check queue
        queue_data = self.step_4_check_queue()
        
        # Step 5: Check messages
        messages = self.step_5_check_messages()
        
        # Summary
        self.display_summary(queue_data, messages)
        
        self.log("Demo completed successfully!", "🎉")
        return True

def main():
    """Main function."""
    demo = StepByStepChatbotDemo()
    demo.run_demonstration()

if __name__ == "__main__":
    main()