import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from jose import jwt
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from app.core.config import settings
from app.main import app
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_async_db
from app.core.security import create_access_token, create_refresh_token
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock

'''
一旦放置
'''

# データベースセッションのモック
@pytest.fixture
def mock_db_session():
    db_session = MagicMock(spec=AsyncSession)
    return db_session

@pytest_asyncio.fixture()
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# @pytest.mark.asyncio
# async def test_check_async_client_instance(async_client):
#     print("!!!!!!!!!!!!!!")
#     print(type(async_client))


@pytest.mark.asyncio
async def test_login_and_access_token(async_client):
    response = await async_client.post(
        "/auth/token",
        data={"email": "test@example.com", "password": "testpassword"},
    )

    print("レスポンス JSON:", response.json())
    assert response.status_code == 200
    json_response = response.json()

    assert "access_token" in json_response
    assert "refresh_token" in json_response
    assert json_response["token_type"] == "bearer"

    access_token = json_response["access_token"]
    refresh_token = json_response["refresh_token"]

    print("取得したアクセストークン:", access_token)
    print("取得したリフレッシュトークン:", refresh_token)

    return access_token, refresh_token


@pytest.mark.asyncio
async def test_refresh_token_expiration(async_client):
    _, refresh_token = await test_login_and_access_token(async_client)

    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    exp_timestamp = payload.get("exp")
    assert exp_timestamp is not None, "リフレッシュトークンに有効期限 (`exp`) が設定されていない"

    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)

    print(f"リフレッシュトークンの有効期限: {exp_datetime}")
    print(f"現在時刻: {now}")

    assert exp_datetime > now, "リフレッシュトークンがすでに期限切れ"

    expected_expiration = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    delta = abs((exp_datetime - expected_expiration).total_seconds())

    assert delta < 10, f"リフレッシュトークンの有効期限が設定と異なる (差: {delta}秒)"


@pytest.mark.asyncio
async def test_login_with_invalid_credentials(async_client):
    response = await async_client.post(
        "/auth/token",
        data={"email": "test3@nothing.jp", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_refresh_token(async_client):
    _, refresh_token = await test_login_and_access_token(async_client)

    response = await async_client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    print("リフレッシュトークン使用時のレスポンス:", response.json())

    assert response.status_code == 200
    json_response = response.json()

    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"

    new_access_token = json_response["access_token"]
    print("新しく発行されたアクセストークン:", new_access_token)


@pytest.mark.asyncio
async def test_access_protected_route(async_client):
    access_token, _ = await test_login_and_access_token(async_client)

    response = await async_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("`/auth/me` のレスポンス:", response.status_code, response.json())
    assert response.status_code == 200
    json_response = response.json()
    print("`/auth/me` レスポンス JSON:", json_response)
    assert json_response["email"] == "test@example.com"
