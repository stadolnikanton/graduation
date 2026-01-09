import pytest

from httpx import ASGITransport, AsyncClient

from sqlalchemy import text


from app.main import app
from app.db import async_session_maker


@pytest.fixture(autouse=True)
async def clean_db():
    """Простая очистка с TRUNCATE CASCADE"""
    async with async_session_maker() as session:
        await session.execute(text("TRUNCATE TABLE files, users CASCADE"))
        await session.commit()
    yield


@pytest.fixture(scope="module", autouse=True)
async def db_connect():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.anyio
async def test_login():
    """Тест для пользователя который прошёл регистрацию"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(  # Создаём пользователя
            "/auth/register",
            json={
                "name": "test",
                "email": "testmail@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )
        response = await ac.post(
            "/auth/login",
            json={"email": "testmail@mail.com", "password": "Vfhnf12999"},
        )

    assert response.status_code == 200
    assert response.json() == {"status": 200}


@pytest.mark.anyio
async def test_login_not_user():
    """Тест пользователя который не прошёл регистрацию и не зарегистрирован"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/auth/login",
            json={"email": "tesfdsgfdstmail@mail.com", "password": "Vfhnf12999"},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}



@pytest.mark.anyio
async def test_login_incorrect_password(db_connect):
    """Тест пользователя с неправильным паролем"""
    
    response = await db_connect.post(
            "/auth/register",
            json={
                "name": "name",
                "email": "testmail@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )

    response = await db_connect.post(
            "/auth/login",
            json={"email": "testmail@mail.com", "password": "qwerty123"},
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}



@pytest.mark.anyio
async def test_register(db_connect):
    """Тест успешной регистрации пользователя"""
    response = await db_connect.post(
            "/auth/register",
            json={
                "name": "testegdsfgsdfgstestset",
                "email": "testtewqtqdfsgsdfgdfswetqwettestmail@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"status": 200}


@pytest.mark.anyio
async def test_register_same_email(db_connect):
    """Тест регистрации с существующим email"""
    response = await db_connect.post(
            "/auth/register",
            json={
                "name": "testegdsfgsdfgstestset",
                "email": "testtewqtqdfsgsdfgdfswetqwettestmail@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )
    response = await db_connect.post(
            "/auth/register",
            json={
                "name": "testegdsfgsdfgstestset",
                "email": "testtewqtqdfsgsdfgdfswetqwettestmail@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


@pytest.mark.anyio
async def test_register_same_name(db_connect):
    """Тест регистрации с существующим именем пользователя"""
    response = await db_connect.post(
            "/auth/register",
            json={
                "name": "testegdsfgsdfgstestset",
                "email": "testtewqtqdfsgsdfgdfswetqwettestmail123@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )
    response = await db_connect.post(
            "/auth/register",
            json={
                "name": "testegdsfgsdfgstestset",
                "email": "testtewqtqdfsgsdfgdfswetqwettestmail@mail.com",
                "password": "Vfhnf12999",
                "password_confirm": "Vfhnf12999",
            },
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "Username already taken"}


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