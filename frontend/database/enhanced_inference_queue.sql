-- Enhanced InferenceQueue table with comprehensive response metrics
CREATE TABLE InferenceQueue (
    id TEXT PRIMARY KEY,
    request_type TEXT NOT NULL CHECK (request_type IN ('meeting_transcription', 'gpt', 'document_analysis', 'compliance_check')),
    input_data TEXT NOT NULL, -- JSON object with request data
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    priority INTEGER DEFAULT 5,
    user_id TEXT REFERENCES Users(id),
    client_id TEXT REFERENCES Clients(id),
    
    -- Timing fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Performance metrics
    queue_wait_time_ms INTEGER, -- Time spent waiting in queue
    processing_time_ms INTEGER, -- Actual AI processing time
    total_time_ms INTEGER, -- Total time from creation to completion
    
    -- AI model metrics
    model_used TEXT, -- Which AI model was used (e.g., 'gpt-4', 'whisper-1')
    model_version TEXT, -- Model version for audit trail
    confidence_score REAL, -- AI confidence in result (0-1)
    
    -- Token/usage metrics
    input_tokens INTEGER, -- Number of input tokens
    output_tokens INTEGER, -- Number of output tokens
    total_tokens INTEGER, -- Total tokens used
    
    -- Cost tracking
    cost_estimate_cents INTEGER, -- Estimated cost in cents
    
    -- Quality metrics
    retry_count INTEGER DEFAULT 0, -- Number of retries attempted
    error_count INTEGER DEFAULT 0, -- Number of errors encountered
    
    -- Results and errors
    result_data TEXT, -- JSON object with AI response
    error_message TEXT,
    
    -- Compliance metrics
    sec_compliant BOOLEAN DEFAULT FALSE, -- Whether result meets SEC requirements
    human_review_required BOOLEAN DEFAULT FALSE, -- Whether human review is needed
    
    -- System metrics
    server_id TEXT, -- Which server processed the request
    memory_used_mb INTEGER, -- Memory usage during processing
    cpu_usage_percent REAL -- CPU usage during processing
);

-- Indexes for performance
CREATE INDEX idx_inference_queue_status ON InferenceQueue(status);
CREATE INDEX idx_inference_queue_user ON InferenceQueue(user_id);
CREATE INDEX idx_inference_queue_created ON InferenceQueue(created_at);
CREATE INDEX idx_inference_queue_request_type ON InferenceQueue(request_type);
CREATE INDEX idx_inference_queue_priority ON InferenceQueue(priority DESC);

-- Composite indexes for common queries
CREATE INDEX idx_inference_queue_status_priority ON InferenceQueue(status, priority DESC);
CREATE INDEX idx_inference_queue_user_status ON InferenceQueue(user_id, status);