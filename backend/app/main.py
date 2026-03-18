from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import auth, accounts, uploads, snapshots, reports, goals

app = FastAPI(title="MoneyMind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(snapshots.router, prefix="/api/snapshots", tags=["snapshots"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"status": "ok"}
