# Baker AI Inference System - Solution Architecture Document

## Executive Summary

The Baker AI Inference System represents a comprehensive, SEC-compliant AI-powered platform designed specifically for wealth management and financial advisory services. Built by Proactive Technology Management (PTM), this system transforms traditional manual compliance processes into an intelligent, automated workflow that maintains regulatory standards while dramatically improving operational efficiency.

The platform serves as a centralized hub for financial advisors, compliance officers, and administrators, providing AI-assisted meeting note processing, portfolio analysis, CRM integration, and comprehensive audit trails. The system operates under strict SEC compliance requirements while delivering measurable ROI through automation and risk reduction.

## System Overview

### Core Value Proposition

The Baker AI system addresses critical challenges in wealth management:

- **Compliance Burden**: Automates SEC-required documentation and review processes
- **Risk Management**: Provides real-time compliance monitoring and flagging
- **Operational Efficiency**: Reduces manual documentation time by 65% while improving accuracy
- **Integration Complexity**: Unifies CRM, portfolio management, and compliance systems
- **Audit Readiness**: Maintains comprehensive, immutable audit trails


### Key Capabilities

1. **AI-Powered Documentation**: Converts meeting recordings and notes into SEC-compliant documentation
2. **Custom GPT Agents**: Specialized AI assistants for different aspects of wealth management
3. **Real-Time Compliance Monitoring**: Continuous assessment against SEC standards
4. **Integrated Workflow Management**: Seamless connection to existing CRM and portfolio systems
5. **Comprehensive Audit Trails**: Complete tracking of all system interactions and decisions

## Architecture Principles

### 1. **Compliance-First Design**

- All components designed with SEC requirements as primary constraint
- Immutable audit logging at every system layer
- Human-in-the-loop validation for critical decisions
- Data retention policies aligned with regulatory requirements


### 2. **AI-Augmented, Human-Supervised**

- AI handles routine processing and analysis
- Human oversight required for final approval and critical decisions
- Confidence scoring with automatic flagging of low-confidence items
- Transparent AI decision-making with full traceability


### 3. **Security by Design**

- AES-256 encryption for all sensitive data
- Multi-layer authentication and authorization
- Secure API endpoints with comprehensive logging
- Network isolation and access controls


### 4. **Scalable Integration Architecture**

- Model Context Protocol (MCP) for external system integration
- RESTful APIs for system interoperability
- Event-driven architecture for real-time processing
- Microservices approach for component isolation


## System Context

### Primary Actors

**Internal Users:**

- **Financial Advisors**: Process meeting notes, access client information, generate reports
- **Compliance Officers**: Review AI-generated content, manage compliance settings, conduct audits
- **Administrators**: Configure system settings, manage user access, oversee integrations

**External Systems:**

- **Redtail CRM**: Client relationship management and data synchronization
- **Albridge Portfolio**: Portfolio data and performance analytics
- **Microsoft Azure**: Authentication and identity management
- **iOS Devices**: Meeting transcription and file upload


### System Boundaries

The Baker AI system operates within the financial services regulatory environment, specifically designed to meet SEC compliance requirements for investment advisors. All data processing, storage, and transmission adheres to financial industry security standards.

## Container Architecture

### Frontend Layer

**Compliant AI UX (React/TypeScript SPA)**[^1]

- **Technology**: React 18, TypeScript, Vite, shadcn/ui components
- **Hosting**: IIS on Windows Server
- **Key Features**:
    - Responsive dashboard with real-time compliance metrics
    - Chat interface with multiple Custom GPT agents
    - Meeting note processing workflow
    - Template completion system
    - Comprehensive audit trail viewer
    - User management and settings

**Key UI Components:**

- **Dashboard**: Real-time KPIs, pending reviews, compliance status
- **Process Notes**: Meeting transcription and AI processing interface
- **Review Queue**: Compliance officer workflow for reviewing AI-generated content
- **Chat Interface**: Multi-threaded conversations with specialized AI agents
- **Templates**: Form-based document generation system
- **Audit Trail**: Complete system activity logging and reporting


### Backend Services Layer

**Compliant AI API Service (Python/FastAPI)**[^1]

- **Technology**: FastAPI, Python 3.11+, Pydantic for data validation
- **Responsibilities**:
    - RESTful API endpoints for frontend interactions
    - Request validation and sanitization
    - Session management and authentication
    - Database query orchestration
    - File upload handling and processing

**LLM Inference Service (Python/PydanticAI)**[^1]

- **Technology**: PydanticAI framework, Python 3.11+
- **Deployment**: Windows Service managed by NSSM
- **Key Components**:
    - **Pydantic AI CustomGPT Agent Executor**: Orchestrates specialized AI agents
    - **Meeting Note Extraction Agent**: Converts raw notes to structured data
    - **Template Filling Agent**: Populates document templates with extracted data
    - **Custom GPT Agents**: Specialized agents for different financial domains


### Integration Layer

**MCP Server Components**[^1]

- **Redtail CRM MCP Server**: Bidirectional CRM data synchronization
- **Albridge MCP Server**: Portfolio data access and analysis
- **Technology**: Python with Model Context Protocol implementation

**RPA Components**[^1]

- **Albridge Portfolio Export RPA**: Power Automate Desktop workflows for data extraction


### Infrastructure Layer

**Local LLM Hosting (Ollama)**[^1]

- **Models**: Gemma3:27b-it-qat, GPT-OSS-20b
- **Purpose**: On-premises AI inference for data privacy and compliance
- **Integration**: HTTP API for model inference requests

**Web Server (IIS)**[^1]

- **Function**: Hosts React frontend and FastAPI backend
- **Configuration**: Reverse proxy for API routing
- **Security**: HTTPS termination and certificate management


## Component Architecture

### Database Schema (SQLite)[^1]

**Core Entities:**

- **Users**: User profiles, roles, permissions, and session management
- **Clients**: Customer information synchronized from Redtail CRM
- **MeetingNotes**: Processed meeting documentation with compliance flags
- **CustomGPTs**: AI agent configurations and specializations
- **Threads/ThreadMessages**: Chat conversation history
- **DocTemplates/DocumentInstances**: Template-based document generation
- **AuditTrailEventLogs**: Comprehensive system activity logging

**Queue Management:**

- **InferenceQueue**: AI processing job management with detailed metrics
- **ResponseQueue**: AI response tracking and status management
- **ReviewQueue**: Human review workflow management

**Configuration:**

- **SystemSettings**: System-wide configuration parameters
- **UserSettings**: User-specific preferences and configurations
- **UserNotificationPreferences**: Notification delivery preferences


### AI Agent Architecture

**Custom GPT Specializations:**[^1]

- **CRM Assistant**: Client relationship management and data queries
- **Portfolio Analyzer**: Investment analysis and performance monitoring
- **Compliance Monitor**: Regulatory compliance checking and flagging
- **General Advisor**: Broad financial advisory assistance
- **Retirement Planner**: Specialized retirement planning support
- **Tax Strategist**: Tax planning and optimization guidance

**Agent Configuration:**

- Specialized system prompts for each agent type
- MCP tool access permissions (Redtail CRM, Albridge Portfolio)
- Custom visual branding and identification
- Usage tracking and performance metrics


## Data Architecture

### Data Flow

1. **Input Processing**:
    - Meeting recordings/notes uploaded via web interface
    - Text extraction and preprocessing
    - Client context retrieval from CRM
2. **AI Processing**:
    - Inference queue job creation
    - LLM processing with confidence scoring
    - Structured data extraction and validation
    - Compliance rule evaluation
3. **Review Workflow**:
    - Automated flagging based on confidence thresholds
    - Human review queue management
    - Approval/rejection workflow with audit logging
4. **Output Generation**:
    - SEC-compliant document generation
    - CRM system updates
    - Audit trail creation and storage

### Data Retention and Compliance

**SEC Requirements:**[^1]

- Meeting notes: 6-year retention period
- Audit trails: 7-year retention recommended
- All system interactions logged with immutable timestamps
- Data encryption at rest (AES-256) and in transit (TLS 1.3)


## Security Architecture

### Authentication and Authorization

**Microsoft Azure Integration:**[^1]

- Azure Active Directory (Entra ID) for user authentication
- App Registration with client secrets for service-to-service communication
- Role-based access control (Advisor, Compliance Officer, Admin, Support)

**Session Management:**

- Secure session tokens with configurable expiration
- IP address and user agent tracking
- Multi-device session monitoring


### Data Protection

**Encryption:**

- AES-256 symmetric encryption for sensitive data at rest
- TLS 1.3 for all network communications
- Environment variable storage for secrets and keys

**Access Controls:**

- Granular user permissions system
- Resource-level access controls
- Audit logging for all access attempts


### Compliance Monitoring

**Real-Time Assessment:**

- Continuous evaluation against SEC requirements
- Automated flagging of potential compliance issues
- Human review requirements for critical decisions
- Comprehensive audit trail generation


## Integration Architecture

### External System Integrations

**Redtail CRM Integration:**[^1]

- **Protocol**: RESTful API with MCP abstraction layer
- **Capabilities**:
    - Read client profiles and relationship data
    - Write meeting notes and activity logs
    - Synchronize contact information and preferences
- **Data Sync**: Real-time bidirectional synchronization
- **Error Handling**: Retry logic with exponential backoff

**Albridge Portfolio Integration:**[^1]

- **Protocol**: File-based integration with RPA automation
- **Capabilities**:
    - Portfolio performance data extraction
    - Asset allocation analysis
    - Risk assessment metrics
- **Automation**: Power Automate Desktop flows for data export
- **Scheduling**: Automated daily data refresh

**Microsoft Azure Services:**

- **Authentication**: Azure AD/Entra ID integration
- **Storage**: Potential future cloud storage integration
- **Monitoring**: Azure Monitor for system telemetry


### API Architecture

**RESTful API Design:**

- Standardized HTTP methods and status codes
- JSON request/response formatting
- Comprehensive input validation
- Rate limiting and throttling
- API versioning strategy

**Model Context Protocol (MCP):**

- Standardized interface for external tool integration
- Pluggable architecture for new system connections
- Security controls for tool access permissions
- Usage tracking and performance monitoring


## Deployment Architecture

### On-Premises Deployment

**Server Configuration:**

- **Operating System**: Windows 11/Server 2019+
- **Web Server**: Internet Information Services (IIS)
- **Application Services**: Windows Services (managed by NSSM)
- **Database**: SQLite for local data storage
- **AI Models**: Ollama for local LLM hosting

**Service Management:**

- **NSSM (Non-Sucking Service Manager)**: Windows service wrapper for Python applications
- **IIS Application Pools**: Isolation and resource management
- **Scheduled Tasks**: Automated maintenance and data synchronization


### Scalability Considerations

**Horizontal Scaling:**

- Load balancing for multiple IIS instances
- Database clustering options for high availability
- Distributed processing for AI inference workloads

**Performance Optimization:**

- Response caching for frequently accessed data
- Connection pooling for database access
- Asynchronous processing for long-running tasks


## Compliance Framework

### SEC Compliance Requirements

**Documentation Standards:**

- All client interactions must be documented
- Investment advice must be traceable and justified
- Conflicts of interest must be disclosed and managed
- Record retention per SEC regulations

**Audit Requirements:**

- Complete audit trails for all system activities
- User access logging and monitoring
- Change management documentation
- Regular compliance assessments


### Implementation Strategy

**Compliance by Design:**

- Built-in SEC requirement validation
- Mandatory human review checkpoints
- Automated compliance rule evaluation
- Real-time risk assessment and flagging

**Quality Assurance:**

- AI confidence scoring with configurable thresholds
- Multi-tier review processes
- Comprehensive testing and validation
- Regular compliance audits


## Technical Stack Summary

### Frontend Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for development and production builds
- **UI Library**: shadcn/ui components with Tailwind CSS
- **State Management**: React Context and hooks
- **Routing**: React Router v6
- **HTTP Client**: Fetch API with custom hooks


### Backend Stack

- **API Framework**: FastAPI with Pydantic validation
- **Language**: Python 3.11+
- **AI Framework**: PydanticAI for agent orchestration
- **Database**: SQLite with custom schemas
- **Authentication**: Azure AD integration
- **File Processing**: Multi-format document parsing


### Infrastructure Stack

- **Web Server**: Microsoft IIS
- **Service Management**: NSSM (Non-Sucking Service Manager)
- **AI Hosting**: Ollama with local LLM models
- **Operating System**: Windows 11/Server
- **Database**: SQLite with comprehensive indexing


### Integration Stack

- **Protocol**: Model Context Protocol (MCP) for external integrations
- **RPA**: Power Automate Desktop for legacy system integration
- **APIs**: RESTful services with OpenAPI documentation
- **Security**: TLS 1.3, AES-256 encryption, Azure AD authentication


## Implementation Considerations

### Deployment Strategy

**Phase 1 - Core Platform:**

- Basic AI processing capabilities
- Essential compliance features
- User authentication and authorization
- Audit logging framework

**Phase 2 - External Integrations:**

- Redtail CRM connectivity
- Albridge portfolio integration
- Enhanced AI agent capabilities
- Advanced reporting features

**Phase 3 - Advanced Features:**

- Additional LLM model support
- Enhanced analytics and insights
- Mobile application development
- Advanced workflow automation


### Operational Considerations

**Monitoring and Alerting:**

- System health monitoring
- Performance metrics tracking
- Compliance violation alerts
- User activity monitoring

**Backup and Recovery:**

- Automated database backups
- Configuration backup procedures
- Disaster recovery planning
- Data integrity validation

**Maintenance and Updates:**

- Regular security updates
- AI model fine-tuning
- Performance optimization
- Feature enhancement deployment


### Risk Mitigation

**Technical Risks:**

- AI model accuracy and reliability
- System integration complexity
- Data migration challenges
- Performance and scalability concerns

**Compliance Risks:**

- Regulatory requirement changes
- Audit preparation and response
- Data privacy and security
- Human oversight requirements

**Mitigation Strategies:**

- Comprehensive testing and validation
- Regular compliance reviews
- Continuous monitoring and alerting
- Expert consultation and training


## Conclusion

The Baker AI Inference System represents a sophisticated, compliance-first approach to AI-powered wealth management. By combining advanced AI capabilities with rigorous SEC compliance requirements, the system delivers transformational value while maintaining the highest standards of regulatory adherence.

The architecture's modular design, comprehensive security framework, and extensive integration capabilities position it as a scalable, future-ready platform for modern wealth management operations. The system's success depends on careful implementation, thorough testing, and ongoing compliance monitoring to ensure it continues to meet both business objectives and regulatory requirements.

This architecture document serves as the foundation for implementation planning, providing detailed guidance for developers, system administrators, compliance officers, and business stakeholders involved in the platform's deployment and operation.
