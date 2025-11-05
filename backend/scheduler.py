"""
Scheduled tasks for TeamPulse
Sends daily check-ins at 9am and reports at 5pm
"""

import schedule
import time
from datetime import datetime
from slack_sdk import WebClient
import config
import database as db

# Initialize Slack client
client = WebClient(token=config.SLACK_BOT_TOKEN)

def send_daily_checkins():
    """Send daily check-in to all users in all workspaces"""
    print(f"[{datetime.now()}] Running daily check-ins...")

    try:
        conn = db.get_db_connection()
        cur = conn.cursor()

        # Get all active workspaces
        cur.execute("SELECT id, slack_team_id FROM workspaces")
        workspaces = cur.fetchall()

        for workspace in workspaces:
            workspace_id = workspace['id']

            # Get all users in workspace
            cur.execute(
                "SELECT slack_user_id FROM users WHERE workspace_id = %s",
                (workspace_id,)
            )
            users = cur.fetchall()

            print(f"  Sending check-ins to {len(users)} users in workspace {workspace_id}")

            for user in users:
                user_id = user['slack_user_id']
                send_checkin_to_user(user_id)

        cur.close()
        conn.close()

        print(f"✅ Daily check-ins sent!")

    except Exception as e:
        print(f"❌ Error sending daily check-ins: {e}")

def send_checkin_to_user(user_id):
    """Send check-in message to specific user"""
    try:
        client.chat_postMessage(
            channel=user_id,
            text="Time for your daily check-in! How are you feeling today?",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "👋 *Daily Check-in*\n\nHow are you feeling today?"
                    }
                },
                {
                    "type": "actions",
                    "block_id": "mood_selection",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "😊 Happy"},
                            "value": "happy",
                            "action_id": "mood_happy",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "😐 Neutral"},
                            "value": "neutral",
                            "action_id": "mood_neutral"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "😟 Stressed"},
                            "value": "stressed",
                            "action_id": "mood_stressed",
                            "style": "danger"
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        print(f"  Error sending to {user_id}: {e}")

def send_daily_reports():
    """Send daily summary to managers"""
    print(f"[{datetime.now()}] Sending daily reports to managers...")

    try:
        conn = db.get_db_connection()
        cur = conn.cursor()

        # Get all active workspaces
        cur.execute("SELECT id, slack_team_id FROM workspaces")
        workspaces = cur.fetchall()

        for workspace in workspaces:
            workspace_id = workspace['id']

            # Get managers in workspace
            managers = db.get_managers(workspace_id)

            if not managers:
                print(f"  No managers in workspace {workspace_id}, skipping")
                continue

            # Get today's stats
            cur.execute(
                """
                SELECT
                    mood,
                    COUNT(*) as count
                FROM checkins
                WHERE workspace_id = %s
                AND DATE(created_at) = CURRENT_DATE
                GROUP BY mood
                ORDER BY count DESC
                """,
                (workspace_id,)
            )
            today_stats = cur.fetchall()

            if not today_stats:
                print(f"  No check-ins today in workspace {workspace_id}, skipping")
                continue

            # Build report message
            total = sum(stat['count'] for stat in today_stats)
            report_text = f"📊 *Daily Team Pulse - {datetime.now().strftime('%B %d, %Y')}*\n\n"
            report_text += f"Total check-ins: {total}\n\n"

            for stat in today_stats:
                mood = stat['mood']
                count = stat['count']
                percentage = round((count / total) * 100, 1)
                emoji = {"happy": "😊", "neutral": "😐", "stressed": "😟"}.get(mood, "❓")
                report_text += f"{emoji} {mood.capitalize()}: {count} ({percentage}%)\n"

            # Send to each manager
            for manager_id in managers:
                try:
                    client.chat_postMessage(
                        channel=manager_id,
                        text=report_text
                    )
                    print(f"  ✅ Report sent to manager {manager_id}")
                except Exception as e:
                    print(f"  ❌ Error sending to manager {manager_id}: {e}")

        cur.close()
        conn.close()

        print(f"✅ Daily reports sent!")

    except Exception as e:
        print(f"❌ Error sending daily reports: {e}")

def run_scheduler():
    """Run the scheduler"""
    print("🕐 TeamPulse Scheduler starting...")

    # Schedule daily check-ins at 9:00 AM
    schedule.every().day.at("09:00").do(send_daily_checkins)

    # Schedule daily reports at 5:00 PM
    schedule.every().day.at("17:00").do(send_daily_reports)

    print(f"✅ Scheduled tasks:")
    print(f"  - Daily check-ins: 09:00")
    print(f"  - Daily reports: 17:00")
    print(f"\n⏰ Waiting for scheduled time...")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    run_scheduler()
