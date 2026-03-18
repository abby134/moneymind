# MoneyMind 💰

> The AI finance coach that remembers everything you forget about your own money.

MoneyMind is a multi-agent personal finance system with long-term memory. Unlike tools that only show you this month's data, MoneyMind builds a persistent understanding of your financial behavior across years — and uses it to give you insights no other tool can.

## What makes it different

| Other tools | MoneyMind |
|-------------|-----------|
| "You spent $400 on food this month" | "You've overspent on food every March for 3 years" |
| Static dashboard | Personalized monthly narrative letter |
| Forgets last month | Remembers your full financial history |
| Generic advice | Advice calibrated to your specific patterns |

## Tech Stack

**Frontend:** Next.js 14 · Tailwind CSS · Vercel
**Backend:** FastAPI · LangGraph · Railway
**Database:** PostgreSQL · Redis
**Memory:** Memory MCP (knowledge graph)
**Agent Tools:** Filesystem MCP · Gmail MCP · Calendar MCP · Brave Search MCP

## Docs

- [PRD — Product Requirements](./docs/PRD.md)
- [ERD — Data Model](./docs/ERD.md)

## Project Structure (coming soon)

```
moneymind/
├── frontend/          # Next.js app
├── backend/           # FastAPI + LangGraph agents
│   ├── agents/        # Planner, Pattern, Anomaly, Goal, Subscription, Fact-Checker
│   ├── mcp/           # MCP client integrations
│   └── api/           # REST endpoints
├── docs/
│   ├── PRD.md
│   └── ERD.md
└── docker-compose.yml
```
