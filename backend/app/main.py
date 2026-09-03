from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import pokemon, sync, drive, bag

app = FastAPI(title="Pokédex Personal", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pokemon.router, prefix="/api/pokemon", tags=["pokemon"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])
app.include_router(drive.router, prefix="/api/drive", tags=["drive"])
app.include_router(bag.router, prefix="/api/bag", tags=["bag"])

@app.get("/api/health")
async def health():
    return {"status": "ok"}
