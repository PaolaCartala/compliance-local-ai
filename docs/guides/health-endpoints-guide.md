# Health Endpoints Guide

## Overview

The Baker Compliant AI system provides comprehensive health monitoring through multiple endpoints that check the status of all critical services.

## Available Endpoints

### Main Health Check
```bash
GET /health/
```
Returns overall system health with detailed status for all services.

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-17T10:30:00Z",
  "version": "1.0.0",
  "database": {
    "status": "HEALTHY",
    "message": "Database connection successful",
    "response_time": 8.5
  },
  "ollama": {
    "status": "HEALTHY", 
    "message": "Ollama service is running",
    "response_time": 12.3
  },
  "queue": {
    "status": "HEALTHY",
    "message": "Queue is operating normally"
  }
}
```

### Individual Service Health Checks

#### Database Health
```bash
GET /health/database
```
Checks database connectivity and table count.

#### Ollama AI Service Health
```bash
GET /health/ollama
```
Verifies Ollama service and available models.

#### Message Queue Health
```bash
GET /health/queue
```
Monitors queue status and job counts.

#### File Storage Health
```bash
GET /health/storage
```
Validates file storage accessibility.

#### MCP Services Health
```bash
GET /health/mcp
```
Checks external MCP service integrations.

## Status Values

- **HEALTHY**: Service is fully operational
- **DEGRADED**: Service has issues but is functional
- **UNHEALTHY**: Service is not working properly
- **NOT_CONFIGURED**: Service is not set up (expected for optional services)

## Usage Examples

### Check Overall System Health
```bash
curl http://localhost:8000/health/
```

### Check Specific Service
```bash
curl http://localhost:8000/health/database
curl http://localhost:8000/health/ollama
```

### Format JSON Output (Windows)
```bash
curl -s http://localhost:8000/health/ | python -m json.tool
```

## Monitoring Integration

These endpoints are designed for:
- Application health monitoring
- Load balancer health checks
- CI/CD pipeline verification
- Automated alerting systems

## Troubleshooting

If any service shows **UNHEALTHY** status:

1. **Database**: Check SQLite file permissions and connectivity
2. **Ollama**: Verify Ollama service is running on port 11434
3. **Queue**: Check for stuck jobs or processing errors
4. **Storage**: Verify file system permissions for uploads directory
5. **MCP**: Check if MCP services are configured and running

For detailed error messages, check the individual service endpoints rather than just the main health endpoint.