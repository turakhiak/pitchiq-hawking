from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth
from ingestion import router as ingestion_router
from agents import router as agents_router
from chat import router as chat_router
from export import router as export_router
from documents import router as documents_router

app = FastAPI(title="Pitchbook Evaluation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
        "https://pitchiq-hawking.vercel.app"  # Production domain - FIXED!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ingestion_router, prefix="/api", tags=["Ingestion"])
app.include_router(agents_router, prefix="/api", tags=["Agents"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(export_router, prefix="/api", tags=["Export"])
app.include_router(documents_router, prefix="/api", tags=["Documents"])

@app.get("/")
async def root():
    return {"message": "Pitchbook Evaluation API is running"}
