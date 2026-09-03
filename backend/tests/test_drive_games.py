import os
from types import SimpleNamespace

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings
from app.database import get_db
from app.main import app
from app.services.auth_service import get_current_user


@pytest.mark.skipif(not os.getenv("RUN_DB_TESTS"), reason="Requires migrated PostgreSQL database")
async def test_game_configs_are_independent_and_legacy_defaults_to_firered():
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            async with AsyncSession(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False) as session:
                async def test_db():
                    yield session

                app.dependency_overrides[get_db] = test_db
                app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=-987654321)
                try:
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                        for game in ["firered", "leafgreen", "emerald", "ruby", "sapphire"]:
                            response = await client.post("/api/drive/config", json={"game": game, "url_or_id": f"https://drive.google.com/file/d/test_{game}/view"})
                            assert response.status_code == 200
                        response = await client.post("/api/drive/config", json={"game": "emerald", "url_or_id": "updated_emerald"})
                        assert response.status_code == 200
                        for game in ["firered", "leafgreen", "emerald", "ruby", "sapphire"]:
                            response = await client.get("/api/drive/config", params={"game": game})
                            assert response.status_code == 200
                            assert response.json()["file_id"] == ("updated_emerald" if game == "emerald" else f"test_{game}")
                            assert response.json()["game"] == game
                        assert (await client.get("/api/drive/config")).json()["file_id"] == "test_firered"
                        assert (await client.post("/api/drive/config", json={"url_or_id": "legacy_firered"})).status_code == 200
                        assert (await client.get("/api/drive/config", params={"game": "firered"})).json()["file_id"] == "legacy_firered"
                        assert (await client.get("/api/drive/config", params={"game": "invalid"})).status_code == 422
                        assert (await client.post("/api/drive/config", json={"game": "invalid", "url_or_id": "test"})).status_code == 422
                        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=-987654322)
                        assert (await client.get("/api/drive/config")).json() is None
                finally:
                    app.dependency_overrides.clear()
                    await transaction.rollback()
    finally:
        await engine.dispose()
