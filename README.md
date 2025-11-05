# 📊 TeamPulse - Daily Wellbeing Check-ins for Slack Teams

A micro-SaaS Slack bot that helps managers understand team wellbeing through simple daily check-ins.

## 🎯 What It Does

- **Daily Check-ins**: Sends private DMs to team members at 9am asking how they feel (😊 😐 😟)
- **Anonymous Responses**: Individual responses are never shared with managers
- **Aggregated Insights**: Managers see team-wide trends and mood distribution
- **Burnout Alerts**: Get notified when team stress levels increase
- **Weekly Reports**: Automatic reports delivered to managers at 5pm

## 🚀 Features

- ✅ 5-second check-ins (just click an emoji)
- 🔒 100% anonymous individual responses
- 📈 Weekly trend analysis
- ⚠️ Proactive burnout alerts
- 📊 Beautiful dashboard with charts
- 💰 Freemium model (free up to 20 users)

## 💰 Pricing Model

| Plan | Price | Users | Features |
|------|-------|-------|----------|
| **Free** | €0/month | Up to 20 | Daily check-ins, basic analytics, 7-day retention |
| **Pro** | €29/month | Up to 100 | Advanced analytics, unlimited retention, custom times |
| **Business** | €79/month | Unlimited | Everything + API access, priority support |

**Revenue Target**: €2k/month = 70 Pro customers or 52 Pro + 20 Business mix

## 🛠️ Tech Stack

**Backend:**
- Python 3.11
- Slack Bolt SDK (Slack bot framework)
- Flask (web server)
- PostgreSQL (database)
- Stripe (payments)

**Frontend:**
- HTML/CSS/JavaScript (landing page)
- Chart.js (dashboard visualizations)

**Deployment:**
- Docker + Docker Compose
- Railway/Render (hosting)
- Vercel (static frontend)

## 📁 Project Structure

```
.
├── backend/
│   ├── app.py                 # Main Slack bot
│   ├── scheduler.py           # Cron jobs for daily messages
│   ├── database.py            # Database operations
│   ├── config.py              # Configuration
│   ├── stripe_integration.py  # Payment handling
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── index.html            # Landing page
│   └── dashboard.html        # Manager dashboard
├── database/
│   └── schema.sql            # Database schema
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🏁 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Slack workspace (for testing)
- Stripe account (for payments)

### 1. Clone Repository

```bash
git clone https://github.com/pedronmbrito/Vercel_test.git
cd Vercel_test
```

### 2. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: `TeamPulse`
4. Select your workspace

**Configure Bot:**
- Go to "OAuth & Permissions"
- Add scopes:
  - `chat:write` (send messages)
  - `im:write` (send DMs)
  - `commands` (slash commands)
  - `users:read` (read user info)
- Install to workspace
- Copy **Bot User OAuth Token**

**Add Slash Command:**
- Go to "Slash Commands"
- Create command: `/teampulse`
- Request URL: `https://your-domain.com/slack/events`

**Enable Events:**
- Go to "Event Subscriptions"
- Request URL: `https://your-domain.com/slack/events`
- Subscribe to: `app_home_opened`

**Copy Credentials:**
- Bot Token: `xoxb-...`
- Signing Secret: (in "Basic Information")

### 3. Setup Environment Variables

```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```env
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-signing-secret
DATABASE_URL=postgresql://teampulse:password@localhost:5432/teampulse
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_BUSINESS_PRICE_ID=price_...
PORT=3000
```

### 4. Setup Database

```bash
# Start PostgreSQL (using Docker)
docker run -d \
  --name teampulse-db \
  -e POSTGRES_DB=teampulse \
  -e POSTGRES_USER=teampulse \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine

# Create schema
psql postgresql://teampulse:password@localhost:5432/teampulse < database/schema.sql
```

### 5. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 6. Run Application

**Terminal 1 - Main App:**
```bash
cd backend
python app.py
```

**Terminal 2 - Scheduler:**
```bash
cd backend
python scheduler.py
```

App will run on http://localhost:3000

### 7. Test It

In Slack:
- Type `/teampulse test` to receive a test check-in
- Click an emoji to respond
- Type `/teampulse dashboard` to see results

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- **postgres**: Database on port 5432
- **app**: Slack bot on port 3000
- **scheduler**: Background cron jobs

## 🚢 Production Deployment

### Option 1: Railway

1. Create account at https://railway.app
2. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```
3. Deploy:
   ```bash
   railway login
   railway init
   railway up
   ```
4. Add PostgreSQL:
   ```bash
   railway add postgres
   ```
5. Set environment variables in Railway dashboard
6. Get public URL and update Slack app URLs

### Option 2: Render

1. Create account at https://render.com
2. Create new **Web Service**:
   - Connect GitHub repo
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && gunicorn app:flask_app`
3. Add PostgreSQL database
4. Add **Background Worker** for scheduler:
   - Start Command: `cd backend && python scheduler.py`
5. Set environment variables
6. Deploy!

### Frontend (Vercel)

```bash
cd frontend
vercel
```

## 🎨 Customization

### Change Check-in Time

Edit `backend/scheduler.py`:
```python
schedule.every().day.at("10:00").do(send_daily_checkins)  # Change to 10am
```

### Add More Moods

Edit `backend/app.py`:
```python
MOOD_OPTIONS = {
    "happy": "😊 Happy",
    "neutral": "😐 Neutral",
    "stressed": "😟 Stressed",
    "excited": "🎉 Excited"  # Add new mood
}
```

### Modify Pricing

Edit `frontend/index.html` and `backend/stripe_integration.py`

## 📊 Database Schema

**Tables:**
- `workspaces` - Slack workspaces using TeamPulse
- `users` - Users in each workspace
- `checkins` - Daily check-in responses
- `settings` - Workspace-specific settings

See `database/schema.sql` for full schema.

## 🔒 Security

- All individual check-in responses are anonymous
- Managers only see aggregated team data
- No individual responses are ever shown
- Stripe handles all payment data (PCI compliant)
- Environment variables for sensitive data
- PostgreSQL with proper indexes

## 📈 Growth Strategy

**Week 1-2: Validation**
- Post in r/SaaS, r/RemoteWork
- Find 5 beta teams
- Get testimonials

**Week 3-4: Launch**
- ProductHunt launch
- Share on Twitter/LinkedIn
- Write blog post about team wellbeing

**Month 2+: Scale**
- SEO content (team wellbeing, burnout prevention)
- Integrations (Microsoft Teams, Google Chat)
- Affiliate program (HR consultants)

**Target**: 10 customers in 30 days → €150-390 MRR

## 🐛 Troubleshooting

**Slack bot not responding:**
- Check Event Subscriptions URL is correct
- Verify Slack token is valid
- Check app logs: `docker-compose logs app`

**Database connection error:**
- Verify PostgreSQL is running
- Check DATABASE_URL is correct
- Test connection: `psql $DATABASE_URL`

**Scheduled messages not sending:**
- Check scheduler is running: `docker-compose logs scheduler`
- Verify cron times in `scheduler.py`
- Check timezone settings

## 📝 License

MIT License - feel free to modify and use for your own projects!

## 🤝 Contributing

PRs welcome! Please open an issue first to discuss changes.

## 📧 Contact

Questions? Email hello@teampulse.app

---

Built with ❤️ for remote teams
