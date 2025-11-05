import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import config

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(config.DATABASE_URL, cursor_factory=RealDictCursor)

def init_workspace(team_id, team_name):
    """Initialize workspace on first install"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO workspaces (slack_team_id, slack_team_name)
            VALUES (%s, %s)
            ON CONFLICT (slack_team_id) DO UPDATE
            SET slack_team_name = EXCLUDED.slack_team_name
            RETURNING id
            """,
            (team_id, team_name)
        )
        workspace_id = cur.fetchone()['id']

        # Create default settings
        cur.execute(
            """
            INSERT INTO settings (workspace_id)
            VALUES (%s)
            ON CONFLICT (workspace_id) DO NOTHING
            """,
            (workspace_id,)
        )

        conn.commit()
        return workspace_id
    finally:
        cur.close()
        conn.close()

def get_or_create_user(slack_user_id, workspace_id, is_manager=False):
    """Get or create user"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO users (slack_user_id, workspace_id, is_manager)
            VALUES (%s, %s, %s)
            ON CONFLICT (slack_user_id, workspace_id) DO UPDATE
            SET is_manager = EXCLUDED.is_manager
            RETURNING id
            """,
            (slack_user_id, workspace_id, is_manager)
        )
        user_id = cur.fetchone()['id']
        conn.commit()
        return user_id
    finally:
        cur.close()
        conn.close()

def save_checkin(user_id, workspace_id, mood, reason=None):
    """Save check-in response"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO checkins (user_id, workspace_id, mood, reason)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (user_id, workspace_id, mood, reason)
        )
        checkin_id = cur.fetchone()['id']
        conn.commit()
        return checkin_id
    finally:
        cur.close()
        conn.close()

def get_workspace_by_team_id(team_id):
    """Get workspace by Slack team ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM workspaces WHERE slack_team_id = %s",
            (team_id,)
        )
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def get_weekly_stats(workspace_id):
    """Get weekly mood statistics for workspace"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Get stats for last 7 days
        cur.execute(
            """
            SELECT
                mood,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
            FROM checkins
            WHERE workspace_id = %s
            AND created_at > NOW() - INTERVAL '7 days'
            GROUP BY mood
            ORDER BY count DESC
            """,
            (workspace_id,)
        )
        mood_stats = cur.fetchall()

        # Get previous week for comparison
        cur.execute(
            """
            SELECT mood, COUNT(*) as count
            FROM checkins
            WHERE workspace_id = %s
            AND created_at BETWEEN NOW() - INTERVAL '14 days' AND NOW() - INTERVAL '7 days'
            GROUP BY mood
            """,
            (workspace_id,)
        )
        previous_week = cur.fetchall()

        return {
            'current_week': mood_stats,
            'previous_week': previous_week
        }
    finally:
        cur.close()
        conn.close()

def get_managers(workspace_id):
    """Get all managers in workspace"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT slack_user_id FROM users
            WHERE workspace_id = %s AND is_manager = TRUE
            """,
            (workspace_id,)
        )
        return [row['slack_user_id'] for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

def get_all_workspace_users(workspace_id):
    """Get all users in workspace"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT slack_user_id FROM users
            WHERE workspace_id = %s
            """,
            (workspace_id,)
        )
        return [row['slack_user_id'] for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()
