# Baker Compliant AI - Inference Service

This service handles AI inference requests for the Baker Compliant AI system using PydanticAI and Ollama models.

## Features

- **Queue-based processing**: Asynchronous request processing with priority management
- **Specialized agents**: Different AI agents for CRM, portfolio analysis, compliance, etc.
- **SEC compliance**: Built-in compliance checking and audit logging
- **Model management**: GPU resource management and model lifecycle
- **MCP ready**: Flexible architecture for future MCP tool integration

## Architecture

```
inference/
├── src/
│   ├── main.py              # Main inference service
│   ├── agents/
│   │   └── chat_agent.py    # PydanticAI chat agents
│   ├── services/
│   │   └── queue_service.py # Queue management
│   ├── database/
│   │   └── service.py       # Database operations
│   └── utils/
│       └── logging.py       # Structured logging
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
# Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
CHAT_MODEL=gemma3:27b-it-qat
VISION_MODEL=gpt-oss-20b

# Database configuration
DATABASE_PATH=../api/database/baker_compliant_ai.db

# Logging level
LOG_LEVEL=INFO
```

## Usage

### Running the Service

```bash
cd inference
python -m src.main
```

### Processing Requests

The service automatically processes requests from the queue table in the database:

1. **Request queuing**: API service adds requests to `inference_queue` table
2. **Agent selection**: Service selects appropriate agent based on Custom GPT specialization
3. **Model inference**: PydanticAI agents process requests using Ollama models
4. **Response storage**: Results stored in database with compliance metadata

### Specialized Agents

- **CRM Agent**: Client relationship management and communication tracking
- **Portfolio Agent**: Investment analysis and portfolio recommendations
- **Compliance Agent**: Regulatory compliance checking and guidance
- **Retirement Agent**: Retirement planning and strategy recommendations
- **Tax Agent**: Tax-efficient investment and planning strategies
- **General Agent**: General financial advisory assistance

## Configuration

### Model Selection

Agents automatically select models based on:
- **Custom GPT specialization**: Different agents for different use cases
- **Request complexity**: Vision models for image attachments
- **Resource availability**: GPU semaphore management

### Queue Management

- **Priority processing**: Higher priority requests processed first
- **Retry logic**: Failed requests automatically retried up to 3 times
- **Resource limits**: GPU semaphore prevents model overloading

### Compliance Features

- **Audit logging**: All requests and responses logged for compliance
- **SEC checking**: Automated compliance validation for responses
- **Human review flags**: High-risk responses flagged for manual review

## Dependencies

- **pydantic-ai**: AI agent framework
- **ollama**: Local LLM model hosting
- **sqlite3**: Database connectivity
- **asyncio**: Asynchronous processing

## Development

### Adding New Agents

1. Add specialization to `ChatAgent._create_specialized_agents()`
2. Define system prompt in `_get_system_prompt()`
3. Configure MCP tools in `_configure_mcp_tools()`

### MCP Integration

The system is designed for future MCP tool integration:

```python
@agent.tool
async def redtail_crm_lookup(client_id: str) -> Dict[str, Any]:
    """Look up client information in Redtail CRM."""
    # MCP tool implementation
    pass
```

## Monitoring

### Queue Statistics

- Real-time queue monitoring via `/api/status` endpoint
- Request processing metrics and timing
- Error rates and retry statistics

### Audit Trail

- All inference requests logged with compliance metadata
- User actions tracked for regulatory requirements
- Model responses analyzed for SEC compliance

## Security

- **Input validation**: All requests validated before processing
- **Output filtering**: Responses checked for compliance violations
- **Audit logging**: Complete request/response audit trail
- **Resource limits**: GPU and memory usage constraints