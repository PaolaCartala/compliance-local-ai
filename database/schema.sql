-- Baker Compliant AI - Extended Database Schema
-- Comprehensive schema including chat system, Custom GPTs, and inference queue

-- ============================================================================
-- USERS AND AUTHENTICATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    azure_user_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('financial_advisor', 'compliance_officer', 'administrator')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_azure_id ON users(azure_user_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================================================
-- CLIENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    redtail_id TEXT UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clients_redtail_id ON clients(redtail_id);
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(last_name, first_name);

-- ============================================================================
-- CUSTOM GPTs
-- ============================================================================

CREATE TABLE IF NOT EXISTS custom_gpts (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    specialization TEXT NOT NULL CHECK (specialization IN ('crm', 'portfolio', 'compliance', 'general', 'retirement', 'tax')),
    color TEXT DEFAULT 'blue',
    icon TEXT DEFAULT 'Brain',
    
    -- MCP Tools Configuration (stored as JSON for flexibility)
    mcp_tools_enabled TEXT DEFAULT '{"redtail_crm": false, "albridge_portfolio": false, "black_diamond": false}',
    
    is_active BOOLEAN DEFAULT TRUE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_custom_gpts_user_id ON custom_gpts(user_id);
CREATE INDEX IF NOT EXISTS idx_custom_gpts_specialization ON custom_gpts(specialization);
CREATE INDEX IF NOT EXISTS idx_custom_gpts_active ON custom_gpts(is_active);

-- ============================================================================
-- CHAT THREADS
-- ============================================================================

CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    title TEXT NOT NULL,
    custom_gpt_id TEXT NOT NULL REFERENCES custom_gpts(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_id TEXT REFERENCES clients(id), -- Optional link to specific client (from C4 design)
    last_message TEXT,
    message_count INTEGER DEFAULT 0,
    is_archived BOOLEAN DEFAULT FALSE,
    tags TEXT DEFAULT '[]', -- JSON array of strings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP -- Added from C4 design
);

CREATE INDEX IF NOT EXISTS idx_threads_user_id ON threads(user_id);
CREATE INDEX IF NOT EXISTS idx_threads_custom_gpt_id ON threads(custom_gpt_id);
CREATE INDEX IF NOT EXISTS idx_threads_client_id ON threads(client_id);
CREATE INDEX IF NOT EXISTS idx_threads_archived ON threads(is_archived);
CREATE INDEX IF NOT EXISTS idx_threads_updated_at ON threads(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_threads_last_message_at ON threads(last_message_at DESC);

-- ============================================================================
-- CHAT MESSAGES
-- ============================================================================

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    thread_id TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    custom_gpt_id TEXT REFERENCES custom_gpts(id),
    user_id TEXT NOT NULL REFERENCES users(id),
    
    -- AI metadata
    confidence_score REAL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    model_used TEXT,
    processing_time_ms INTEGER,
    
    -- Compliance
    compliance_flags TEXT DEFAULT '[]', -- JSON array of strings
    sec_compliant BOOLEAN DEFAULT TRUE,
    human_review_required BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_compliance ON messages(sec_compliant, human_review_required);

-- ============================================================================
-- FILE ATTACHMENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_attachments (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    original_name TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    is_processed BOOLEAN DEFAULT FALSE,
    user_id TEXT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_attachments_message_id ON file_attachments(message_id);
CREATE INDEX IF NOT EXISTS idx_file_attachments_user_id ON file_attachments(user_id);
CREATE INDEX IF NOT EXISTS idx_file_attachments_mime_type ON file_attachments(mime_type);

-- ============================================================================
-- MCP TOOL INTERACTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS mcp_tool_interactions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    tool_name TEXT NOT NULL CHECK (tool_name IN ('redtail-crm', 'albridge-portfolio', 'black-diamond')),
    action TEXT NOT NULL,
    input_data TEXT, -- JSON
    output_data TEXT, -- JSON
    success BOOLEAN NOT NULL,
    error_message TEXT,
    execution_time_ms INTEGER,
    user_id TEXT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mcp_interactions_message_id ON mcp_tool_interactions(message_id);
CREATE INDEX IF NOT EXISTS idx_mcp_interactions_tool_name ON mcp_tool_interactions(tool_name);
CREATE INDEX IF NOT EXISTS idx_mcp_interactions_user_id ON mcp_tool_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_mcp_interactions_success ON mcp_tool_interactions(success);

-- ============================================================================
-- INFERENCE QUEUE SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS inference_queue (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    message_id TEXT REFERENCES messages(id),
    custom_gpt_id TEXT REFERENCES custom_gpts(id), -- Added: Link to Custom GPT configuration
    request_type TEXT NOT NULL CHECK (request_type IN ('chat', 'meeting_transcription', 'document_analysis', 'compliance_check')),
    input_data TEXT NOT NULL, -- JSON object with request data
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    user_id TEXT NOT NULL REFERENCES users(id),
    client_id TEXT REFERENCES clients(id),
    
    -- Timing fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Performance metrics
    queue_wait_time_ms INTEGER,
    processing_time_ms INTEGER,
    total_time_ms INTEGER,
    
    -- AI model metrics
    model_used TEXT,
    model_version TEXT,
    confidence_score REAL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    
    -- Token/usage metrics
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    
    -- Cost tracking
    cost_estimate_cents INTEGER,
    
    -- Quality metrics
    retry_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Results and errors  
    response_content TEXT, -- AI response content
    response_metadata TEXT, -- JSON object with response metadata
    error_message TEXT,
    
    -- Compliance metrics
    sec_compliant BOOLEAN DEFAULT FALSE,
    human_review_required BOOLEAN DEFAULT FALSE,
    
    -- System metrics
    server_id TEXT,
    memory_used_mb INTEGER,
    cpu_usage_percent REAL
);

CREATE INDEX IF NOT EXISTS idx_inference_queue_status ON inference_queue(status);
CREATE INDEX IF NOT EXISTS idx_inference_queue_priority ON inference_queue(priority, created_at);
CREATE INDEX IF NOT EXISTS idx_inference_queue_user_id ON inference_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_inference_queue_request_type ON inference_queue(request_type);
CREATE INDEX IF NOT EXISTS idx_inference_queue_created_at ON inference_queue(created_at);
CREATE INDEX IF NOT EXISTS idx_inference_queue_message_id ON inference_queue(message_id);
CREATE INDEX IF NOT EXISTS idx_inference_queue_custom_gpt_id ON inference_queue(custom_gpt_id);

-- ============================================================================
-- AUDIT TRAIL EVENT LOGS (IMMUTABLE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_trail_event_logs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    event_type TEXT NOT NULL, -- 'user_action', 'ai_inference', 'mcp_interaction', 'system_event'
    user_id TEXT REFERENCES users(id),
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    client_id TEXT REFERENCES clients(id),
    
    -- Event details (JSON)
    event_data TEXT, -- JSON object with action-specific data
    
    -- Compliance information
    sec_compliant BOOLEAN DEFAULT TRUE,
    compliance_notes TEXT,
    
    -- System information
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT,
    
    -- Immutable timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_trail_event_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_trail_event_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_trail_event_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_client_id ON audit_trail_event_logs(client_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_trail_event_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_trail_event_logs(event_type);

-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_by TEXT REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configuration values
INSERT OR IGNORE INTO system_config (key, value, description) VALUES
('compliance_confidence_threshold', '0.8', 'Minimum confidence score for SEC compliance'),
('human_review_threshold', '0.7', 'Confidence threshold below which human review is required'),
('max_context_messages', '10', 'Maximum number of previous messages to include in context'),
('file_retention_days', '2190', 'File retention period in days (6 years)'),
('audit_retention_days', '2555', 'Audit log retention period in days (7 years)'),
('encryption_enabled', 'false', 'Whether AES-256 encryption is enabled for sensitive data');

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Update threads.updated_at when a message is added
CREATE TRIGGER IF NOT EXISTS update_thread_on_message_insert
AFTER INSERT ON messages
BEGIN
    UPDATE threads 
    SET 
        updated_at = CURRENT_TIMESTAMP,
        message_count = message_count + 1,
        last_message = CASE 
            WHEN length(NEW.content) > 100 
            THEN substr(NEW.content, 1, 100) || '...'
            ELSE NEW.content
        END
    WHERE id = NEW.thread_id;
END;

-- Update custom_gpts.updated_at when modified
CREATE TRIGGER IF NOT EXISTS update_custom_gpt_timestamp
AFTER UPDATE ON custom_gpts
BEGIN
    UPDATE custom_gpts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update users.updated_at when modified
CREATE TRIGGER IF NOT EXISTS update_user_timestamp
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for thread summaries with Custom GPT information
CREATE VIEW IF NOT EXISTS thread_summaries AS
SELECT 
    t.id,
    t.title,
    t.message_count,
    t.last_message,
    t.is_archived,
    t.created_at,
    t.updated_at,
    t.user_id,
    cg.name as custom_gpt_name,
    cg.specialization,
    cg.color,
    cg.icon
FROM threads t
JOIN custom_gpts cg ON t.custom_gpt_id = cg.id;

-- View for message summaries with user and Custom GPT information
CREATE VIEW IF NOT EXISTS message_summaries AS
SELECT 
    m.id,
    m.thread_id,
    m.content,
    m.role,
    m.confidence_score,
    m.sec_compliant,
    m.human_review_required,
    m.created_at,
    u.display_name as user_name,
    cg.name as custom_gpt_name,
    cg.specialization
FROM messages m
JOIN users u ON m.user_id = u.id
LEFT JOIN custom_gpts cg ON m.custom_gpt_id = cg.id;

-- View for queue statistics
CREATE VIEW IF NOT EXISTS queue_statistics AS
SELECT 
    status,
    request_type,
    COUNT(*) as count,
    AVG(queue_wait_time_ms) as avg_wait_time_ms,
    AVG(processing_time_ms) as avg_processing_time_ms,
    AVG(confidence_score) as avg_confidence_score
FROM inference_queue 
GROUP BY status, request_type;