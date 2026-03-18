# MoneyMind — Product Requirements Document

## 1. Overview

**Product Name:** MoneyMind
**Tagline:** The AI finance coach that remembers everything you forget about your own money.
**Target User:** Individuals aged 25–45 who want to understand their financial patterns over time, not just this month's spending.
**Problem:** Mint shut down in 2023. Existing tools (YNAB, Copilot) show current data but have no longitudinal memory or behavioral insight. No tool today can tell you "you've broken this promise to yourself three years in a row."

---

## 2. User Stories

### Core
- As a user, I want to upload my monthly bank statement CSV and get actionable insights **compared to my history**, not just this month in isolation.
- As a user, I want to know which subscriptions I'm paying for that I no longer use.
- As a user, I want to track progress toward financial goals (e.g., house down payment) across months and years.
- As a user, I want to receive a monthly "financial letter" that feels personal, not like a generic dashboard.

### Memory-specific
- As a user, I want the system to remember that I always overspend in December so it can warn me in November.
- As a user, I want to see my net worth trend over the past 12 months, not just today.
- As a user, I want the system to remember goals I set previously and tell me if I'm on track or drifting.

---

## 3. Features

### MVP (v1.0)

| Feature | Description |
|---------|-------------|
| CSV Upload | Upload bank statement in any standard CSV format |
| Auto Categorization | AI classifies each transaction (food, rent, subscriptions, etc.) |
| Subscription Detection | Identifies recurring charges, flags ones unused >60 days |
| Pattern Detection | Cross-references current month vs memory of past months |
| Goal Tracking | Set financial goals; agent tracks progress each month |
| Monthly Report | Personalized narrative report delivered via email |
| Memory Store | All insights and snapshots persisted via Memory MCP |
| Dashboard | Next.js web dashboard showing trends, categories, goals |

### v2.0 (Post-MVP)

| Feature | Description |
|---------|-------------|
| Multi-account | Support multiple banks / credit cards |
| Budget Recommendations | AI-suggested budgets based on personal history |
| Seasonal Alerts | "You tend to overspend in Q4 — here's your prep plan" |
| Net Worth Tracker | Track assets + liabilities over time |
| Export | PDF report generation |

---

## 4. Agent Architecture

### Four-Layer Pipeline

```
Layer 1 — Orchestration
  Planner Agent
  - Parses uploaded CSV
  - Queries Memory MCP for user history
  - Dispatches tasks to Layer 2 workers

Layer 2 — Parallel Workers (all run concurrently)
  Pattern Agent     → compares this month vs historical memory
  Anomaly Agent     → finds unusual or new charges
  Goal Agent        → checks progress on all active goals
  Subscription Agent→ scans for recurring charges + zombie subs

Layer 3 — Validation
  Fact-Checker Agent
  - Re-runs all numerical claims independently
  - Verifies pattern claims have ≥3 months of supporting data
  - Blocks unsupported assertions from reaching the user

Layer 4 — Output
  Writer Agent      → generates narrative monthly letter
  Memory Agent      → writes new snapshot to Memory MCP
  Action Agent      → sends email (Gmail MCP), sets reminders (Calendar MCP)
```

### MCP Servers Used

| MCP Server | Purpose |
|-----------|---------|
| Filesystem MCP | Read uploaded CSV files |
| Memory MCP | Persist financial snapshots, patterns, goals across sessions |
| Gmail MCP | Send monthly report email to user |
| Calendar MCP | Set payment reminders, goal check-in alerts |
| Brave Search MCP | Look up current savings rates, credit card offers |

---

## 5. User Flow

```
1. User registers → sets up profile (income range, financial goals)
2. User uploads CSV on the 1st of each month
3. System runs full agent pipeline (~2–3 min)
4. User receives email: "Your MoneyMind Report — [Month]"
5. User visits dashboard to explore details
6. Agent stores snapshot to Memory MCP
7. Next month, Memory MCP provides context for richer analysis
```

---

## 6. Deployment

### Frontend
| Item | Choice |
|------|--------|
| Framework | Next.js 14 (App Router) |
| Hosting | Vercel |
| Styling | Tailwind CSS + shadcn/ui |
| Charts | Recharts |
| Auth | NextAuth.js (GitHub / Google OAuth) |

### Backend
| Item | Choice |
|------|--------|
| Framework | FastAPI (Python) |
| Hosting | **Railway** — chosen for: simple deploy from GitHub, built-in PostgreSQL, free tier, supports long-running agent tasks, no cold-start issues |
| Agent Orchestration | LangGraph |
| Task Queue | Celery + Redis (for async agent pipeline) |
| File Storage | Local filesystem (MVP) → S3 (v2) |

### Database
| Item | Choice |
|------|--------|
| Primary DB | PostgreSQL (Railway managed) |
| Memory Store | Memory MCP (knowledge graph, JSON file) |
| Cache | Redis (also on Railway) |

### Architecture Diagram

```
User Browser
    │
    ▼
Next.js (Vercel)
    │  REST API calls
    ▼
FastAPI (Railway)
    ├── PostgreSQL (Railway)     ← structured data
    ├── Redis (Railway)          ← task queue
    └── Memory MCP               ← agent memory (knowledge graph)
         │
         ▼
    LangGraph Agent Pipeline
    ├── Filesystem MCP
    ├── Brave Search MCP
    ├── Gmail MCP
    └── Calendar MCP
```

### Environment Variables

**Frontend (Vercel)**
```
NEXT_PUBLIC_API_URL=https://api.moneymind.app
NEXTAUTH_SECRET=
NEXTAUTH_URL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

**Backend (Railway)**
```
DATABASE_URL=
REDIS_URL=
ANTHROPIC_API_KEY=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
BRAVE_API_KEY=
MEMORY_MCP_PATH=./memory/moneymind.json
```

---

## 7. Monetization

| Tier | Price | Features |
|------|-------|---------|
| Free | $0 | 3 months history, basic categorization, no email delivery |
| Pro | $12/mo | Unlimited history, full agent pipeline, monthly email, goal tracking |
| Annual | $99/yr | Pro features + priority processing |

**Comparable:** YNAB $14.99/mo, Copilot $13/mo — MoneyMind competes on the memory and insight angle.
