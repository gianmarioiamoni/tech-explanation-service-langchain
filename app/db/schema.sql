-- Database schema for quota management system
-- This schema tracks user requests and token usage for rate limiting

-- Users table: stores basic user information
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    hf_username TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0
);

-- Request log: detailed log of each LLM request
CREATE TABLE IF NOT EXISTS request_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    topic TEXT NOT NULL,
    rag_used BOOLEAN DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT 1,
    error_msg TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Daily quotas: aggregated daily usage per user
CREATE TABLE IF NOT EXISTS daily_quotas (
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    requests_count INTEGER DEFAULT 0,
    tokens_count INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_request_log_user_timestamp 
    ON request_log(user_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_daily_quotas_date 
    ON daily_quotas(date);

