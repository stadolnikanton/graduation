import pytest

from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_login(db_connect):
    """Тест для пользователя который прошёл регистрацию"""
    response = await db_connect.post(
            "/auth/register",
            json={
                "name": "test_login_user",
                "email": "login@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )
    response = await db_connect.post(
            "/auth/login",
            json={"email": "login@mail.com", "password": "Vfhnf12999"},
        )

    assert response.status_code == 200
    assert response.json() == {"status": 200}


@pytest.mark.anyio
async def test_login_not_user(db_connect):
    """Тест пользователя который не зарегистрирован"""
    response = await db_connect.post(
            "/auth/login",
            json={"email": "nonexistent@mail.com", "password": "Vfhnf12999"},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@pytest.mark.anyio
async def test_login_incorrect_password(db_connect):
    """
    Тест пользователя с неправильным паролем.
    Этот тест использует фикстуру db_connect из conftest.py
    """
    await db_connect.post(
            "/auth/register",
            json={
                "name": "wrong_pass_user",
                "email": "wrongpass@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )

    response = await db_connect.post(
            "/auth/login",
            json={"email": "wrongpass@mail.com", "password": "qwerty123"},
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}