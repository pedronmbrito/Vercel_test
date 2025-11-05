"""
Stripe payment integration for TeamPulse
Handles subscriptions and webhooks
"""

import os
from flask import Blueprint, request, jsonify
import stripe
import database as db

# Initialize Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Pricing
PRICING = {
    "free": {
        "name": "Free",
        "price": 0,
        "max_users": 20
    },
    "pro": {
        "name": "Pro",
        "price_id": os.environ.get("STRIPE_PRO_PRICE_ID"),
        "price": 29,
        "max_users": 100
    },
    "business": {
        "name": "Business",
        "price_id": os.environ.get("STRIPE_BUSINESS_PRICE_ID"),
        "price": 79,
        "max_users": -1  # unlimited
    }
}

# Create Blueprint
payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session"""
    try:
        data = request.json
        team_id = data.get('team_id')
        plan = data.get('plan', 'pro')  # pro or business

        if plan not in ['pro', 'business']:
            return jsonify({'error': 'Invalid plan'}), 400

        # Get workspace
        workspace = db.get_workspace_by_team_id(team_id)
        if not workspace:
            return jsonify({'error': 'Workspace not found'}), 404

        # Create or get Stripe customer
        if workspace.get('stripe_customer_id'):
            customer_id = workspace['stripe_customer_id']
        else:
            customer = stripe.Customer.create(
                metadata={'team_id': team_id, 'workspace_id': workspace['id']}
            )
            customer_id = customer.id

            # Update workspace with customer ID
            conn = db.get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE workspaces SET stripe_customer_id = %s WHERE id = %s",
                (customer_id, workspace['id'])
            )
            conn.commit()
            cur.close()
            conn.close()

        # Create checkout session
        price_id = PRICING[plan]['price_id']

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=os.environ.get('SUCCESS_URL', 'https://teampulse.app/success'),
            cancel_url=os.environ.get('CANCEL_URL', 'https://teampulse.app/cancel'),
            metadata={
                'team_id': team_id,
                'workspace_id': workspace['id'],
                'plan': plan
            }
        )

        return jsonify({'url': session.url})

    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/api/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session)

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_update(subscription)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_cancellation(subscription)

    return jsonify({'status': 'success'})

def handle_successful_payment(session):
    """Handle successful payment"""
    try:
        workspace_id = session['metadata'].get('workspace_id')
        plan = session['metadata'].get('plan')
        subscription_id = session.get('subscription')

        if not workspace_id:
            print("No workspace_id in session metadata")
            return

        # Update workspace with subscription
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE workspaces
            SET plan = %s, stripe_subscription_id = %s
            WHERE id = %s
            """,
            (plan, subscription_id, int(workspace_id))
        )
        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Workspace {workspace_id} upgraded to {plan}")

    except Exception as e:
        print(f"Error handling successful payment: {e}")

def handle_subscription_update(subscription):
    """Handle subscription update"""
    try:
        customer_id = subscription['customer']

        # Find workspace by customer ID
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM workspaces WHERE stripe_customer_id = %s",
            (customer_id,)
        )
        result = cur.fetchone()

        if result:
            workspace_id = result['id']

            # Check subscription status
            status = subscription['status']

            if status == 'active':
                print(f"✅ Subscription active for workspace {workspace_id}")
            else:
                print(f"⚠️ Subscription status '{status}' for workspace {workspace_id}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error handling subscription update: {e}")

def handle_subscription_cancellation(subscription):
    """Handle subscription cancellation"""
    try:
        customer_id = subscription['customer']

        # Find workspace by customer ID
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM workspaces WHERE stripe_customer_id = %s",
            (customer_id,)
        )
        result = cur.fetchone()

        if result:
            workspace_id = result['id']

            # Downgrade to free plan
            cur.execute(
                """
                UPDATE workspaces
                SET plan = 'free', stripe_subscription_id = NULL
                WHERE id = %s
                """,
                (workspace_id,)
            )
            conn.commit()

            print(f"⬇️ Workspace {workspace_id} downgraded to free plan")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error handling subscription cancellation: {e}")

@payments_bp.route('/api/cancel-subscription', methods=['POST'])
def cancel_subscription():
    """Cancel subscription"""
    try:
        data = request.json
        team_id = data.get('team_id')

        # Get workspace
        workspace = db.get_workspace_by_team_id(team_id)
        if not workspace:
            return jsonify({'error': 'Workspace not found'}), 404

        subscription_id = workspace.get('stripe_subscription_id')
        if not subscription_id:
            return jsonify({'error': 'No active subscription'}), 400

        # Cancel subscription
        stripe.Subscription.delete(subscription_id)

        return jsonify({'status': 'success', 'message': 'Subscription cancelled'})

    except Exception as e:
        print(f"Error cancelling subscription: {e}")
        return jsonify({'error': str(e)}), 500
