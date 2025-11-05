-- TeamPulse Database Schema

CREATE TABLE IF NOT EXISTS workspaces (
    id SERIAL PRIMARY KEY,
    slack_team_id VARCHAR(50) UNIQUE NOT NULL,
    slack_team_name VARCHAR(255),
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    plan VARCHAR(20) DEFAULT 'free', -- free, pro, business
    stripe_customer_id VARCHAR(100),
    stripe_subscription_id VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    slack_user_id VARCHAR(50) NOT NULL,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    is_manager BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(slack_user_id, workspace_id)
);

CREATE TABLE IF NOT EXISTS checkins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    mood VARCHAR(20) NOT NULL, -- happy, neutral, stressed
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE UNIQUE,
    checkin_time TIME DEFAULT '09:00:00',
    report_time TIME DEFAULT '17:00:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    enabled BOOLEAN DEFAULT TRUE
);

-- Indexes for performance
CREATE INDEX idx_checkins_workspace ON checkins(workspace_id);
CREATE INDEX idx_checkins_created_at ON checkins(created_at);
CREATE INDEX idx_users_workspace ON users(workspace_id);
