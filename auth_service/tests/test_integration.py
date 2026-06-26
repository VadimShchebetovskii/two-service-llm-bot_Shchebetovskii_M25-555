import pytest


@pytest.mark.anyio
class TestAuthIntegration:
    """Интеграционные тесты Auth Service."""

    async def test_register_success(self, async_client):
        response = await async_client.post(
            "/auth/register",
            json={"email": "shchebetovsky@email.com", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "shchebetovsky@email.com"
        assert "id" in data
        assert "role" in data

    async def test_register_duplicate_email(self, async_client):
        # Первая регистрация
        await async_client.post(
            "/auth/register",
            json={"email": "shchebetovsky@email.com", "password": "password123"}
        )

        # Вторая регистрация с тем же email
        response = await async_client.post(
            "/auth/register",
            json={"email": "shchebetovsky@email.com", "password": "password123"}
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    async def test_login_success(self, async_client):
        # Регистрация
        await async_client.post(
            "/auth/register",
            json={"email": "shchebetovsky@email.com", "password": "password123"}
        )

        # Логин
        response = await async_client.post(
            "/auth/login",
            data={"username": "shchebetovsky@email.com", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_password(self, async_client):
        # Регистрация
        await async_client.post(
            "/auth/register",
            json={"email": "shchebetovsky@email.com", "password": "password123"}
        )

        # Логин с неверным паролем
        response = await async_client.post(
            "/auth/login",
            data={"username": "shchebetovsky@email.com", "password": "wrong_password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_login_user_not_found(self, async_client):
        # Логин несуществующего пользователя
        response = await async_client.post(
            "/auth/login",
            data={"username": "nonexistent@email.com", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_me_success(self, async_client):
        # Регистрация
        await async_client.post(
            "/auth/register",
            json={"email": "shchebetovsky@email.com", "password": "password123"}
        )

        # Логин
        login = await async_client.post(
            "/auth/login",
            data={"username": "shchebetovsky@email.com", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login.json()["access_token"]

        # Me
        response = await async_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "shchebetovsky@email.com"
        assert "id" in data
        assert "role" in data

    async def test_me_without_token(self, async_client):
        response = await async_client.get("/auth/me")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    async def test_me_with_invalid_token(self, async_client):
        response = await async_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token"}
        )
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
