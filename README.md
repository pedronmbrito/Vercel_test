# 🔗 Shortify - URL Shortener SaaS

A modern, beautiful URL shortener built with Next.js 14, TypeScript, and Tailwind CSS. Perfect example of a mini SaaS application!

## ✨ Features

- **URL Shortening**: Transform long URLs into short, shareable links
- **Analytics Dashboard**: Track clicks and monitor link performance
- **Real-time Stats**: View total URLs, total clicks, and average engagement
- **Modern UI**: Beautiful gradient design with dark mode support
- **Fast & Reliable**: Built on Next.js 14 with App Router
- **File-based Storage**: Simple JSON storage (no database required)
- **Responsive Design**: Works perfectly on desktop and mobile

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## 📦 Deployment

### Deploy to Vercel (Recommended)

1. Push your code to GitHub
2. Import your repository on [Vercel](https://vercel.com)
3. Vercel will automatically detect Next.js and deploy
4. Done! Your mini SaaS is live!

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

### Build for Production

```bash
npm run build
npm start
```

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **ID Generation**: nanoid
- **Deployment**: Vercel

## 📁 Project Structure

```
shortify/
├── app/
│   ├── [shortId]/        # Dynamic redirect routes
│   ├── api/
│   │   ├── shorten/      # URL shortening API
│   │   └── analytics/    # Analytics API
│   ├── dashboard/        # Analytics dashboard
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Homepage
│   └── globals.css       # Global styles
├── lib/
│   └── db.ts            # File-based database
├── data/                # JSON storage (auto-generated)
└── public/              # Static assets
```

## 🎯 How It Works

1. **Shorten URL**: User enters a long URL on the homepage
2. **Generate Short ID**: System creates a unique 6-character ID using nanoid
3. **Store & Return**: URL mapping is saved, short link is returned
4. **Redirect**: When someone visits the short link, they're redirected to the original URL
5. **Track**: Each click is counted and displayed in the analytics dashboard

## 🎨 Features Overview

### Homepage
- Clean, modern interface
- URL input with validation
- One-click copy to clipboard
- Feature highlights with icons

### Dashboard
- Total URLs created
- Total clicks across all links
- Average clicks per URL
- Detailed table of all shortened URLs
- Creation timestamps
- Click counts per link

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👨‍💻 Author

Built with ❤️ using Claude Code

---

**Note**: This is a demo application. For production use, consider:
- Adding a real database (PostgreSQL, MongoDB, etc.)
- Implementing user authentication
- Adding custom short URLs
- Link expiration
- Advanced analytics (geolocation, devices, etc.)
- Rate limiting
- Custom domains
