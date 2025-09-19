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
        self.usage_limits = None  # Will be set during initialization
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
            # Initialize Ollama models using OpenAI-compatible API with conservative settings
            from pydantic_ai.settings import ModelSettings
            from pydantic_ai.usage import UsageLimits
            
            # Maximum capacity settings optimized for GTX 5090 (32GB VRAM)
            # Supporting gpt-oss-20b (~14GB) + llama3.2-vision-11b (~12GB) concurrent usage
            model_settings = ModelSettings(
                max_tokens=4096,   # Maximum token generation for comprehensive responses
                temperature=0.3,   # Balanced creativity while maintaining accuracy
                timeout=180        # Extended timeout for complex processing with high-capacity models
            )
            
            # High-capacity UsageLimits for maximum throughput testing environment
            usage_limits = UsageLimits(
                request_limit=10,             # Allow multiple requests for complex conversations
                input_tokens_limit=8192,      # Large input context for comprehensive document analysis
                output_tokens_limit=4096,     # Maximum output for detailed responses
                total_tokens_limit=12288,     # High total budget for complex conversations
                tool_calls_limit=5            # Allow multiple tool calls for comprehensive analysis
            )
            
            self.models["chat"] = OpenAIChatModel(
                model_name=chat_model,
                provider=OllamaProvider(base_url=base_url),
                settings=model_settings  # Apply conservative settings
            )
            
            self.models["vision"] = OpenAIChatModel(
                model_name=vision_model,
                provider=OllamaProvider(base_url=base_url),
                settings=model_settings  # Apply conservative settings
            )
            
            # Store usage limits for later use in agent runs
            self.usage_limits = usage_limits
            
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
        # Comprehensive system prompts optimized for high-capacity models
        base_prompts = {
            "crm": """You are an expert CRM assistant for financial advisors. You have deep knowledge of client relationship management, data analysis, and financial advisory best practices. 

Your capabilities include:
- Analyzing client portfolios and providing insights
- Tracking client communications and follow-ups
- Identifying opportunities for portfolio optimization
- Ensuring compliance with SEC regulations
- Generating comprehensive client reports

Provide detailed, professional responses that help advisors make informed decisions. Use specific examples and actionable recommendations when possible.""",
            
            "portfolio": """You are an expert portfolio analysis assistant specializing in wealth management and investment strategies. You have comprehensive knowledge of:

- Asset allocation strategies and modern portfolio theory
- Risk assessment and management techniques
- Market analysis and economic indicators
- Regulatory compliance (SEC, FINRA guidelines)
- Performance attribution and reporting

Your responses should be:
- Detailed and analytically rigorous
- Backed by financial theory and best practices
- Compliant with regulatory standards
- Actionable for investment decisions

Provide comprehensive analysis with specific recommendations, risk assessments, and compliance considerations.""",
            
            "compliance": """You are an expert compliance officer assistant specializing in SEC regulations, FINRA guidelines, and wealth management compliance. Your expertise includes:

- Regulatory requirements analysis and interpretation
- Risk assessment and mitigation strategies  
- Audit trail documentation and reporting
- Client communication compliance review
- Investment recommendation compliance validation

Your responses must be:
- Precise and regulation-specific
- Include relevant rule citations when applicable
- Identify potential compliance risks
- Provide actionable compliance guidance
- Maintain detailed documentation standards

Focus on proactive compliance management and risk prevention.""",
            
            "general": """You are a comprehensive financial advisory assistant with expertise across all aspects of wealth management. Your knowledge spans:

- Client relationship management
- Investment analysis and portfolio management
- Regulatory compliance and risk management
- Financial planning and retirement strategies
- Tax optimization and estate planning

Provide thorough, professional responses that demonstrate deep financial expertise while maintaining strict adherence to regulatory requirements. Tailor your advice to the specific context and provide actionable insights.""",
            
            "retirement": """You are an expert retirement planning specialist with comprehensive knowledge of:

- Retirement income strategies and withdrawal planning
- Social Security optimization techniques
- Tax-efficient retirement account management
- Estate planning integration with retirement goals
- Healthcare cost planning and long-term care considerations
- Required minimum distribution strategies

Your responses should provide:
- Detailed retirement projection analysis
- Tax optimization strategies specific to retirement
- Risk management for retirement portfolios
- Comprehensive planning recommendations
- Regulatory compliance considerations for retirement accounts

Focus on creating sustainable, tax-efficient retirement income strategies.""",
            
            "tax": """You are an expert tax planning specialist for high-net-worth individuals and families. Your expertise includes:

- Advanced tax optimization strategies
- Estate and gift tax planning
- Business succession planning tax implications
- Charitable giving tax strategies  
- Investment tax efficiency and harvesting
- Multi-state tax considerations

Provide comprehensive tax analysis including:
- Specific tax code references when relevant
- Multi-year tax planning strategies
- Risk/benefit analysis of tax strategies
- Coordination with overall financial plan
- Regulatory compliance considerations

Focus on proactive tax planning that integrates with overall wealth management strategies."""
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
                deps=context,
                usage_limits=self.usage_limits  # Apply usage limits to prevent server overload
            )
            
            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Determine confidence and compliance
            confidence_score = self._calculate_confidence_score(result, custom_gpt)
            sec_compliant = self._check_sec_compliance(result, specialization)
            human_review_required = confidence_score < 0.7 or specialization == "compliance"
            
            # Generate compliance flags based on analysis
            compliance_flags = []
            if not sec_compliant:
                compliance_flags.append("SEC_NON_COMPLIANT")
            if human_review_required:
                compliance_flags.append("HUMAN_REVIEW_REQUIRED")
            if confidence_score < 0.5:
                compliance_flags.append("LOW_CONFIDENCE")
            
            # Extract any MCP interactions (placeholder)
            mcp_interactions = []  # TODO: Extract from agent run context
            
            response = {
                "success": True,
                "content": str(result.output),
                "confidence_score": confidence_score,
                "model_used": f"{specialization}_{self.models['chat'].model_name}",
                "processing_time_ms": processing_time_ms,
                "mcp_interactions": mcp_interactions,
                "compliance_flags": compliance_flags,
                "sec_compliant": sec_compliant,
                "human_review_required": human_review_required,
                "input_tokens": getattr(result.usage(), "input_tokens", 0) if hasattr(result, "usage") else 0,
                "output_tokens": getattr(result.usage(), "output_tokens", 0) if hasattr(result, "usage") else 0,
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
            
            # Handle specific PydanticAI exceptions
            error_type = type(e).__name__
            if "UsageLimitExceeded" in error_type:
                logger.warning(
                    "Usage limit exceeded",
                    message_id=message_id,
                    error=str(e),
                    processing_time_ms=processing_time_ms
                )
                error_message = "Response limit exceeded. Please try a simpler request."
            elif "UnexpectedModelBehavior" in error_type:
                logger.error(
                    "Model behavior error",
                    message_id=message_id,
                    error=str(e),
                    processing_time_ms=processing_time_ms
                )
                error_message = "AI model encountered an error. Please try again."
            else:
                logger.error(
                    "Chat processing failed",
                    message_id=message_id,
                    error=str(e),
                    processing_time_ms=processing_time_ms,
                    exc_info=True
                )
                error_message = f"Processing failed: {str(e)}"
            
            # Return error response
            return {
                "success": False,
                "content": error_message,
                "confidence_score": 0.0,
                "model_used": f"{specialization}_error",
                "processing_time_ms": processing_time_ms,
                "mcp_interactions": [],
                "compliance_flags": ["ERROR", "HUMAN_REVIEW_REQUIRED"],
                "sec_compliant": False,
                "human_review_required": True,
                "input_tokens": 0,
                "output_tokens": 0,
                "error": str(e)
            }
    
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
        
        # Add simple custom instructions if available
        if custom_gpt.get("system_prompt"):
            # Truncate to prevent long prompts
            custom_prompt = custom_gpt['system_prompt'][:200]
            prompt_parts.append(f"Instructions: {custom_prompt}")
        
        # Add minimal conversation context (last 2 messages only)
        if context_messages:
            for msg in context_messages[-2:]:  # Only last 2 messages to reduce complexity
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:100]  # Truncate content
                prompt_parts.append(f"{role}: {content}")
        
        # Add current user message
        prompt_parts.append(f"User: {user_message}")
        
        # Simple response instruction
        prompt_parts.append("Respond briefly and helpfully:")
        
        return "\n".join(prompt_parts)  # Use single newlines instead of double
    
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
        content = str(result.output).lower()
        
        # Basic compliance checks
        if "guaranteed returns" in content or "risk-free" in content:
            return False
        
        if specialization == "compliance":
            return True  # Compliance agent responses are inherently compliant
        
        return True  # Default to compliant for now