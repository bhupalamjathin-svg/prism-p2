from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

app = FastAPI(
    title="Samsung PRISM — Smart Guided Troubleshooting Engine",
    description="Deterministic Neuro-Symbolic Backend: Version-Aware Planning, Deeplink Resolution, Symbolic Guardrails & Sub-300ms Fast-Path Caching.",
    version="1.0.0"
)

# Enable CORS for local development (Streamlit, React, or mobile clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "engine": "Samsung PRISM Smart Guided Troubleshooting Engine",
        "role": "P1 Backend + Catalog Lead",
        "status": "online",
        "endpoints": {
            "troubleshoot": "POST /troubleshoot",
            "execute_fix": "POST /fix",
            "list_scenarios": "GET /scenarios",
            "metrics": "GET /metrics",
            "docs": "/docs"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-09-24T22:30:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
