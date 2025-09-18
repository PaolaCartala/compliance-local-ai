"""
Chat agent implementation using PydanticAI for Baker Compliant AI.

This agent handles chat conversations with Custom GPT configurations,
integrates with Ollama models, and provides flexible MCP tool support.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import KnownModelName
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider

from inference.src.utils.config import InferenceSettings
from inference.src.utils.logging import logger, log_inference_operation, log_model_operation


class ChatContext(BaseModel):
    """Context for chat agent execution."""
    message_id: str
    thread_id: str
    custom_gpt_id: str
    custom_gpt_config: Dict[str, Any]
    user_id: str
    conversation_history: List[Dict[str, Any]]
    attachments: List[Dict[str, Any]]
    mcp_tools_enabled: Dict[str, bool]


class ChatResponse(BaseModel):
    """Response from chat agent."""
    content: str
    confidence_score: float
    model_used: str
    processing_time_ms: int
    mcp_interactions: List[Dict[str, Any]]
    sec_compliant: bool
    human_review_required: bool


class ChatAgent:
    """
    Specialized chat agent for financial advisory conversations.
    
    Uses PydanticAI to orchestrate conversations with Custom GPT configurations,
    model selection based on specialization, and MCP tool integrations.
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.models: Dict[str, OpenAIChatModel] = {}
        self.initialized = False
    
    async def initialize(
        self,
        base_url: str,
        chat_model: str,
        vision_model: str
    ) -> None:
        """
        Initialize the chat agent with Ollama models.
        
        Args:
            base_url: Ollama service base URL
            chat_model: Primary chat model name
            vision_model: Vision-capable model name
        """
        try:
            # Initialize Ollama models using OpenAI-compatible API
            self.models["chat"] = OpenAIChatModel(
                model_name=chat_model,
                provider=OllamaProvider(base_url=base_url)
            )
            
            self.models["vision"] = OpenAIChatModel(
                model_name=vision_model,
                provider=OllamaProvider(base_url=base_url)
            )
            
            # Create specialized agents for each Custom GPT type
            await self._create_specialized_agents()
            
            self.initialized = True
            logger.info(
                "Chat agent initialized successfully",
                chat_model=chat_model,
                vision_model=vision_model,
                base_url=base_url,
                agent_count=len(self.agents)
            )
            
        except Exception as e:
            logger.error("Failed to initialize chat agent", error=str(e), exc_info=True)
            raise
    
    async def _create_specialized_agents(self) -> None:
        """Create PydanticAI agents for each specialization type."""
        
        # CRM Specialist Agent
        self.agents["crm"] = Agent(
            model=self.models["chat"],
            system_prompt=self._get_system_prompt("crm")
        )
        
        # Portfolio Analyst Agent
        self.agents["portfolio"] = Agent(
            model=self.models["chat"],
            system_prompt=self._get_system_prompt("portfolio")
        )
        
        # Compliance Officer Agent
        self.agents["compliance"] = Agent(
            model=self.models["chat"],
            system_prompt=self._get_system_prompt("compliance")
        )
        
        # General Purpose Agent
        self.agents["general"] = Agent(
            model=self.models["chat"],
            system_prompt=self._get_system_prompt("general")
        )
        
        # Retirement Planning Agent
        self.agents["retirement"] = Agent(
            model=self.models["chat"],
            system_prompt=self._get_system_prompt("retirement")
        )
        
        # Tax Planning Agent
        self.agents["tax"] = Agent(
            model=self.models["chat"],
            system_prompt=self._get_system_prompt("tax")
        )
        
        # Add MCP tools to agents (placeholder for now)
        for agent_type, agent in self.agents.items():
            await self._configure_mcp_tools(agent, agent_type)
    
    def _get_system_prompt(self, specialization: str) -> str:
        """
        Get the base system prompt for a specialization.
        
        Args:
            specialization: Agent specialization type
            
        Returns:
            Base system prompt string
        """
        base_prompts = {
            "crm": """You are a specialized CRM assistant for financial advisors at Baker Group. 
You help manage client relationships, track communications, and ensure proper documentation for SEC compliance. 
Always prioritize client confidentiality and regulatory requirements. 
When recommending actions, ensure they align with SEC and FINRA regulations.""",
            
            "portfolio": """You are a specialized portfolio analysis assistant for wealth management at Baker Group. 
You analyze investment portfolios, provide performance insights, and make SEC-compliant investment recommendations 
based on client risk tolerance and objectives. Always consider diversification, risk management, and 
regulatory compliance in your recommendations.""",
            
            "compliance": """You are a specialized compliance assistant for Baker Group financial advisory services. 
You ensure all communications, recommendations, and documentation meet SEC and FINRA requirements. 
You flag potential compliance issues and provide regulatory guidance. 
Always err on the side of caution and require human review for sensitive matters.""",
            
            "general": """You are a helpful AI assistant for Baker Group financial services. 
You provide general assistance while maintaining strict compliance with financial industry regulations. 
Always defer to specialized advisors for specific financial recommendations and ensure all advice 
is compliant with SEC requirements.""",
            
            "retirement": """You are a specialized retirement planning assistant for Baker Group. 
You help clients plan for retirement by analyzing their current financial situation, 
projecting future needs, and recommending appropriate savings and investment strategies. 
Always consider tax implications and regulatory requirements.""",
            
            "tax": """You are a specialized tax planning assistant for Baker Group financial advisors. 
You provide guidance on tax-efficient investment strategies, retirement planning, and estate planning. 
Always ensure recommendations comply with current tax law and SEC regulations."""
        }
        
        return base_prompts.get(specialization, base_prompts["general"])
    
    async def _configure_mcp_tools(self, agent: Agent, agent_type: str) -> None:
        """
        Configure MCP tools for an agent (placeholder implementation).
        
        Args:
            agent: PydanticAI agent to configure
            agent_type: Type of agent for tool selection
        """
        # TODO: Implement MCP tool configuration once MCP servers are ready
        # This will add tools like:
        # - @agent.tool for Redtail CRM operations
        # - @agent.tool for Albridge portfolio data
        # - @agent.tool for compliance checking
        
        logger.debug(f"MCP tools configuration placeholder for {agent_type} agent")
    
    async def process_chat(
        self,
        message_id: str,
        thread_id: str,
        custom_gpt: Dict[str, Any],
        user_message: str,
        context_messages: List[Dict[str, Any]],
        attachments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message using the appropriate specialized agent.
        
        Args:
            message_id: Unique message identifier
            thread_id: Thread context identifier
            custom_gpt: Custom GPT configuration
            user_message: User's message content
            context_messages: Previous conversation context
            attachments: Message attachments if any
            
        Returns:
            Dict containing the AI response and metadata
        """
        if not self.initialized:
            raise RuntimeError("Chat agent not initialized")
        
        start_time = datetime.utcnow()
        
        try:
            # Determine which agent to use
            specialization = custom_gpt.get("specialization", "general")
            agent = self.agents.get(specialization, self.agents["general"])
            
            # Parse MCP tools configuration
            mcp_tools_enabled = json.loads(custom_gpt.get("mcp_tools_enabled", "{}"))
            
            # Create context for the agent
            context = ChatContext(
                message_id=message_id,
                thread_id=thread_id,
                custom_gpt_id=custom_gpt["id"],
                custom_gpt_config=custom_gpt,
                user_id=custom_gpt["user_id"],
                conversation_history=context_messages,
                attachments=attachments or [],
                mcp_tools_enabled=mcp_tools_enabled
            )
            
            # Build the conversation prompt
            conversation_prompt = self._build_conversation_prompt(
                custom_gpt=custom_gpt,
                user_message=user_message,
                context_messages=context_messages
            )
            
            # Run the agent
            logger.debug(
                "Running chat agent",
                message_id=message_id,
                specialization=specialization,
                context_length=len(context_messages)
            )
            
            result = await agent.run(
                conversation_prompt,
                deps=context
            )
            
            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Determine confidence and compliance
            confidence_score = self._calculate_confidence_score(result, custom_gpt)
            sec_compliant = self._check_sec_compliance(result, specialization)
            human_review_required = confidence_score < 0.7 or specialization == "compliance"
            
            # Extract any MCP interactions (placeholder)
            mcp_interactions = []  # TODO: Extract from agent run context
            
            response = {
                "content": str(result.data),
                "confidence_score": confidence_score,
                "model_used": f"{specialization}_{self.models['chat'].model_name}",
                "processing_time_ms": processing_time_ms,
                "mcp_interactions": mcp_interactions,
                "sec_compliant": sec_compliant,
                "human_review_required": human_review_required,
                "input_tokens": getattr(result, "usage", {}).get("input_tokens", 0),
                "output_tokens": getattr(result, "usage", {}).get("output_tokens", 0),
            }
            
            logger.info(
                "Chat processing completed",
                message_id=message_id,
                specialization=specialization,
                processing_time_ms=processing_time_ms,
                confidence_score=confidence_score,
                sec_compliant=sec_compliant
            )
            
            return response
            
        except Exception as e:
            processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.error(
                "Chat processing failed",
                message_id=message_id,
                error=str(e),
                processing_time_ms=processing_time_ms,
                exc_info=True
            )
            raise
    
    def _build_conversation_prompt(
        self,
        custom_gpt: Dict[str, Any],
        user_message: str,
        context_messages: List[Dict[str, Any]]
    ) -> str:
        """
        Build the conversation prompt including context and custom instructions.
        
        Args:
            custom_gpt: Custom GPT configuration
            user_message: Current user message
            context_messages: Previous conversation context
            
        Returns:
            Formatted conversation prompt
        """
        prompt_parts = []
        
        # Add custom system prompt
        if custom_gpt.get("system_prompt"):
            prompt_parts.append(f"Custom Instructions: {custom_gpt['system_prompt']}")
        
        # Add conversation context
        if context_messages:
            prompt_parts.append("Previous conversation:")
            for msg in context_messages[-5:]:  # Last 5 messages for context
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                prompt_parts.append(f"{role.title()}: {content}")
        
        # Add current user message
        prompt_parts.append(f"User: {user_message}")
        
        # Add response instruction
        prompt_parts.append("Please provide a helpful, accurate, and SEC-compliant response:")
        
        return "\n\n".join(prompt_parts)
    
    def _calculate_confidence_score(self, result: Any, custom_gpt: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the AI response.
        
        Args:
            result: Agent result object
            custom_gpt: Custom GPT configuration
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # TODO: Implement proper confidence calculation based on:
        # - Model certainty
        # - Response length and coherence
        # - Specialization match
        # - MCP tool success rates
        
        base_confidence = 0.85  # Default confidence
        
        # Adjust based on specialization
        specialization = custom_gpt.get("specialization", "general")
        if specialization == "compliance":
            base_confidence = 0.75  # Lower for compliance due to higher stakes
        elif specialization in ["crm", "portfolio"]:
            base_confidence = 0.80  # Moderate for data-driven tasks
        
        return base_confidence
    
    def _check_sec_compliance(self, result: Any, specialization: str) -> bool:
        """
        Check if the response meets SEC compliance requirements.
        
        Args:
            result: Agent result object
            specialization: Agent specialization type
            
        Returns:
            True if response is SEC compliant
        """
        # TODO: Implement proper compliance checking:
        # - Scan for prohibited language
        # - Check for required disclosures
        # - Validate investment advice disclaimers
        # - Ensure appropriate risk warnings
        
        # For now, assume compliance based on specialization
        content = str(result.data).lower()
        
        # Basic compliance checks
        if "guaranteed returns" in content or "risk-free" in content:
            return False
        
        if specialization == "compliance":
            return True  # Compliance agent responses are inherently compliant
        
        return True  # Default to compliant for now