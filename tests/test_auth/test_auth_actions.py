import pytest


@pytest.mark.anyio
async def test_logout(db_connect):
    """Тест успешного logout"""
    await db_connect.post(
        "/v1/auth/register",
        json={
            "username": "test_valid_user",
            "first_name": "test_valid",
            "last_name": "_user",
            "email": "login@mail.com",
            "password": "TestPassword",
            "password_confirm": "TestPassword",
        },
    )

    response = await db_connect.post("/v1/auth/logout")

    assert response.status_code == 200
    assert db_connect.cookies.get("access_token") is None
    assert db_connect.cookies.get("refresh_token") is None


@pytest.mark.anyio
async def test_refresh_token(db_connect):
    """Тест обновления токена"""
    await db_connect.post(
        "/v1/auth/register",
        json={
            "username": "test_valid_user",
            "first_name": "test_valid",
            "last_name": "_user",
            "email": "login@mail.com",
            "password": "TestPassword",
            "password_confirm": "TestPassword",
        },
    )

    response = await db_connect.post("/v1/auth/refresh")

    assert response.status_code == 200
    assert db_connect.cookies.get("access_token") is not None
    assert db_connect.cookies.get("refresh_token") is not None
