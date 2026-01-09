import pytest


@pytest.mark.anyio
async def test_logout(db_connect):
    """Тест успешного logout"""
    await db_connect.post(
        "/auth/register",
        json={
            "name": "logout_test_user",
            "email": "logout_test@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )
    
    response = await db_connect.post("/auth/logout")
    
    assert response.status_code == 200
    assert response.json() == {"status": 200, "message": "Logged out successfully"}


@pytest.mark.anyio
async def test_refresh_token(db_connect):
    """Тест обновления токена"""
    await db_connect.post(
        "/auth/register",
        json={
            "name": "refresh_test_user",
            "email": "refresh_test@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )
    response = await db_connect.post("/auth/refresh")
    
    assert response.status_code == 200
    assert response.json() == {"status": 200}