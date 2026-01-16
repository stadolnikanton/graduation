import pytest


@pytest.mark.anyio
async def test_register(db_connect):
    """Тест успешной регистрации пользователя"""
    response = await db_connect.post(
        "/auth/register",
        json={
            "name": "test_user_reg",
            "email": "test_reg@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": 200}


@pytest.mark.anyio
async def test_register_same_email(db_connect):
    """Тест регистрации с существующим email"""
    # Первый запрос
    await db_connect.post(
        "/auth/register",
        json={
            "name": "user1",
            "email": "duplicate@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )
    # Второй запрос с тем же email
    response = await db_connect.post(
        "/auth/register",
        json={
            "name": "user2",
            "email": "duplicate@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


@pytest.mark.anyio
async def test_register_same_name(db_connect):
    """Тест регистрации с существующим именем пользователя"""
    await db_connect.post(
        "/auth/register",
        json={
            "name": "unique_name",
            "email": "email1@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )
    response = await db_connect.post(
        "/auth/register",
        json={
            "name": "unique_name",
            "email": "email2@mail.com",
            "password": "Vfhnf12999",
            "password_confirm": "Vfhnf12999",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Username already taken"}

