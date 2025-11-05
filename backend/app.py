import os
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
import config
import database as db
from stripe_integration import payments_bp

# Initialize Slack app
app = App(
    token=config.SLACK_BOT_TOKEN,
    signing_secret=config.SLACK_SIGNING_SECRET
)

# Initialize Flask for web server
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Register Stripe payment routes
flask_app.register_blueprint(payments_bp)

# Mood options
MOOD_OPTIONS = {
    "happy": "😊 Happy",
    "neutral": "😐 Neutral",
    "stressed": "😟 Stressed"
}

# ================== INSTALLATION ==================

@app.event("app_home_opened")
def handle_app_home_opened(event, client):
    """Handle when user opens the app home"""
    user_id = event["user"]

    try:
        client.views_publish(
            user_id=user_id,
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to TeamPulse! 👋*\n\nWe help managers understand team wellbeing through simple daily check-ins."
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*How it works:*\n• Every morning, team members receive a private check-in\n• They select their mood: 😊 😐 😟\n• Managers get anonymous aggregated insights\n• No individual responses are shared"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*For Managers:*\nUse `/teampulse dashboard` to view team insights"
                        }
                    }
                ]
            }
        )
    except Exception as e:
        print(f"Error publishing home view: {e}")

# ================== CHECK-IN MESSAGE ==================

def send_checkin_to_user(user_id, client):
    """Send daily check-in message to user"""
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
        return True
    except Exception as e:
        print(f"Error sending check-in to {user_id}: {e}")
        return False

# ================== MOOD SELECTION HANDLERS ==================

@app.action("mood_happy")
@app.action("mood_neutral")
@app.action("mood_stressed")
def handle_mood_selection(ack, body, client):
    """Handle mood button click"""
    ack()

    user_id = body["user"]["id"]
    team_id = body["team"]["id"]
    action = body["actions"][0]
    mood = action["value"]

    # Get workspace
    workspace = db.get_workspace_by_team_id(team_id)
    if not workspace:
        workspace_id = db.init_workspace(team_id, body.get("team", {}).get("domain", "Unknown"))
    else:
        workspace_id = workspace['id']

    # Get or create user
    user_db_id = db.get_or_create_user(user_id, workspace_id)

    # Ask for optional reason
    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "checkin_reason_modal",
                "private_metadata": f"{user_db_id}|{workspace_id}|{mood}",
                "title": {"type": "plain_text", "text": "Optional: Tell us more"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "close": {"type": "plain_text", "text": "Skip"},
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"You selected: *{MOOD_OPTIONS[mood]}*"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "reason_block",
                        "optional": True,
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "reason_input",
                            "multiline": True,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "What's contributing to how you feel? (optional, anonymous)"
                            }
                        },
                        "label": {"type": "plain_text", "text": "Anything you'd like to share?"}
                    }
                ]
            }
        )
    except Exception as e:
        print(f"Error opening modal: {e}")
        # Fallback: save without reason
        db.save_checkin(user_db_id, workspace_id, mood)
        send_confirmation(client, user_id, mood)

@app.view("checkin_reason_modal")
def handle_checkin_submission(ack, body, client):
    """Handle check-in modal submission"""
    ack()

    # Parse private metadata
    metadata = body["view"]["private_metadata"]
    user_db_id, workspace_id, mood = metadata.split("|")
    user_db_id = int(user_db_id)
    workspace_id = int(workspace_id)

    # Get optional reason
    values = body["view"]["state"]["values"]
    reason = None
    if "reason_block" in values and "reason_input" in values["reason_block"]:
        reason_value = values["reason_block"]["reason_input"].get("value")
        if reason_value:
            reason = reason_value

    # Save check-in
    db.save_checkin(user_db_id, workspace_id, mood, reason)

    # Send confirmation
    user_id = body["user"]["id"]
    send_confirmation(client, user_id, mood)

def send_confirmation(client, user_id, mood):
    """Send confirmation message after check-in"""
    messages = {
        "happy": "Great to hear! 😊 Keep up the positive energy!",
        "neutral": "Thanks for checking in! 😐",
        "stressed": "Thanks for sharing. Remember to take breaks when needed. 😟"
    }

    try:
        client.chat_postMessage(
            channel=user_id,
            text=f"✅ Check-in recorded! {messages.get(mood, 'Thanks!')}"
        )
    except Exception as e:
        print(f"Error sending confirmation: {e}")

# ================== MANAGER DASHBOARD ==================

def generate_dashboard_message(workspace_id):
    """Generate dashboard message for managers"""
    stats = db.get_weekly_stats(workspace_id)

    if not stats['current_week']:
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📊 *Team Pulse - Weekly Report*\n\n_No check-ins recorded this week yet._"
                    }
                }
            ]
        }

    # Build mood breakdown
    mood_text = "*This Week's Mood Breakdown:*\n"
    total_checkins = sum(stat['count'] for stat in stats['current_week'])

    for stat in stats['current_week']:
        mood = stat['mood']
        count = stat['count']
        percentage = stat['percentage']
        emoji = {"happy": "😊", "neutral": "😐", "stressed": "😟"}.get(mood, "❓")
        mood_text += f"{emoji} {mood.capitalize()}: {count} responses ({percentage}%)\n"

    # Calculate trend
    prev_stressed = next((s['count'] for s in stats['previous_week'] if s['mood'] == 'stressed'), 0)
    curr_stressed = next((s['count'] for s in stats['current_week'] if s['mood'] == 'stressed'), 0)

    trend = ""
    if curr_stressed > prev_stressed:
        diff = curr_stressed - prev_stressed
        trend = f"\n⚠️ *Alert:* {diff} more stressed response(s) than last week"
    elif curr_stressed < prev_stressed:
        diff = prev_stressed - curr_stressed
        trend = f"\n✅ *Positive:* {diff} fewer stressed response(s) than last week"

    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📊 *Team Pulse - Weekly Report*\n\n{mood_text}{trend}\n\n_Total check-ins: {total_checkins}_"
                }
            }
        ]
    }

@app.command("/teampulse")
def handle_teampulse_command(ack, command, client):
    """Handle /teampulse slash command"""
    ack()

    user_id = command["user_id"]
    team_id = command["team_id"]
    text = command.get("text", "").strip().lower()

    # Get workspace
    workspace = db.get_workspace_by_team_id(team_id)
    if not workspace:
        client.chat_postEphemeral(
            channel=command["channel_id"],
            user=user_id,
            text="❌ TeamPulse is not set up for this workspace yet."
        )
        return

    if text == "dashboard" or text == "":
        # Generate and send dashboard
        dashboard = generate_dashboard_message(workspace['id'])
        client.chat_postEphemeral(
            channel=command["channel_id"],
            user=user_id,
            **dashboard
        )
    elif text == "test":
        # Send test check-in to user
        send_checkin_to_user(user_id, client)
        client.chat_postEphemeral(
            channel=command["channel_id"],
            user=user_id,
            text="✅ Test check-in sent to you via DM!"
        )
    else:
        client.chat_postEphemeral(
            channel=command["channel_id"],
            user=user_id,
            text="Usage:\n• `/teampulse dashboard` - View team insights\n• `/teampulse test` - Send test check-in to yourself"
        )

# ================== FLASK ROUTES ==================

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """Handle Slack events"""
    return handler.handle(request)

@flask_app.route("/slack/install", methods=["GET"])
def slack_install():
    """Handle Slack app installation"""
    # This would normally use Slack's OAuth flow
    # For now, return simple success page
    return "<h1>TeamPulse Installation</h1><p>Please add TeamPulse to your Slack workspace.</p>"

@flask_app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "TeamPulse"}

@flask_app.route("/", methods=["GET"])
def home():
    """Home page"""
    return "<h1>TeamPulse Bot</h1><p>Slack bot for team wellbeing check-ins.</p>"

# ================== MAIN ==================

if __name__ == "__main__":
    print(f"⚡️ TeamPulse bot is running on port {config.PORT}")
    flask_app.run(host="0.0.0.0", port=config.PORT)
