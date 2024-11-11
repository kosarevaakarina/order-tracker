import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from starlette.testclient import TestClient
from auth.hash_password import HashPassword
from crud.user_crud import UserCrud
from main import app
from models.users import User
from schemas.user_schema import UserCreate, UserUpdate


@pytest.fixture
def get_access_token_and_superuser(mocker):
    mock_user = User(
        username="superuser",
        email="superuser@mail.com",
        hashed_password="hashed_password",
        is_superuser=True
    )
    mock_user.id = 1
    mocker.patch('crud.user_crud.UserCrud.get_user', return_value=mock_user)
    mocker.patch('auth.hash_password.HashPassword.verify', return_value=True)
    data = {
        "id": mock_user.id,
        "username": mock_user.username,
        "email": mock_user.email,
        "password": "Password123!"
    }
    with TestClient(app) as client:
        response = client.post("/v1/api/users/token", data=data)
    return response.json()["access_token"], mock_user


@pytest.fixture
def get_access_token_and_user(mocker):
    mock_user = User(
        username="user1",
        email="user1@mail.com",
        hashed_password="hashed_password",
        is_superuser=False
    )
    mock_user.id = 1
    mocker.patch.object(UserCrud, 'get_user', return_value=mock_user)
    mocker.patch.object(HashPassword, 'verify', return_value=True)
    data = {
        "id": mock_user.id,
        "username": mock_user.username,
        "email": mock_user.email,
        "password": "Password123!"
    }
    with TestClient(app) as client:
        response = client.post("/v1/api/users/token", data=data)
    return response.json()["access_token"], mock_user


@pytest.mark.asyncio
class TestUserRegistration:
    async def test_register(self, mocker):
        mock_user_data = UserCreate(
            username="user1",
            email='user1@mail.ru',
            password="Password123!!"
        )

        mock_user = User(
            username=mock_user_data.username,
            email=mock_user_data.email
        )
        mock_user.id = 1
        mock_user.password = HashPassword.bcrypt(mock_user_data.password)
        mocker.patch('crud.user_crud.UserCrud.create_user', return_value=mock_user)
        mocker.patch('config.db.get_session', return_value=AsyncMock())

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/api/users/register",
                json=mock_user_data.model_dump(),
            )
            response_data = response.json()
            assert response.status_code == 200
            assert response_data["username"] == mock_user.username
            assert response_data["email"] == mock_user.email


@pytest.mark.asyncio
class TestUserLogin:
    async def test_login_success(self, mocker):
        mock_user = User(
            username="test",
            hashed_password="hashed_password"
        )
        mocker.patch.object(UserCrud, 'get_user', return_value=mock_user)
        mocker.patch.object(HashPassword, 'verify', return_value=True)

        data = {
            "username": "testuser",
            "password": "Password123!"
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/v1/api/users/token", data=data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    async def test_login_user_not_found(self, mocker):
        mock_user = {
            "username": "testuser",
            "password": "Password123!"
        }
        mocker.patch.object(UserCrud, 'get_user', return_value=None)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/v1/api/users/token", data=mock_user)
        assert response.status_code == 404
        assert response.json()["detail"] == "Not found: User does not exist"

    async def test_login_invalid_password(self, mocker):
        mock_user = User(
            username="tester",
            hashed_password="hashed_password"
        )
        mocker.patch.object(UserCrud, 'get_user', return_value=mock_user)
        mocker.patch.object(HashPassword, 'verify', return_value=False)
        data = {
            "username": "testuser",
            "password": "Password123!"
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/v1/api/users/token", data=data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Invalid password"

    async def test_login_missing_fields(self):
        data = {}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/token", data=data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Not Found"


@pytest.mark.asyncio
class TestGetAllUsers:
    async def test_get_all_users_success_superuser(self, mocker, get_access_token_and_superuser):
        mock_user = get_access_token_and_superuser[1]
        mock_users = [
            MagicMock(id=2, username="user1", email="email1@gmail.com"),
            MagicMock(id=3, username="user2", email="email2@gmail.com")
        ]
        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_users', return_value=mock_users)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"Authorization": f"Bearer {get_access_token_and_superuser[0]}"}
            response = await client.get('/v1/api/users/', headers=headers)

        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == len(mock_users)
        assert response_data[0]['username'] == mock_users[0].username
        assert response_data[1]['username'] == mock_users[1].username

    async def test_get_all_users_forbidden(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]
        mock_users = [
            MagicMock(id=mock_user.id, username=mock_user.username, email=mock_user.email),
            MagicMock(id=2, username="user2", email="email2@gmail.com")
        ]
        mocker.patch('services.check_permissions.check_permissions_users', return_value=True)
        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_users', return_value=mock_users)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"Authorization": f"Bearer {get_access_token_and_user[0]}"}
            response = await client.get('/v1/api/users/', headers=headers)
        assert response.status_code == 403
        assert response.json()["detail"] == 'FORBIDDEN: No permission to perform this action'

    async def test_get_all_users_invalid_token(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                '/v1/api/users/',
                headers={"Authorization": f"Bearer invalid_token"}
            )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetUserDetail:
    async def test_get_user_detail_success(self, mocker, get_access_token_and_superuser):
        mock_user = get_access_token_and_superuser[1]
        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_user', return_value=mock_user)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                '/v1/api/users/1',
                headers={"Authorization": f"Bearer {get_access_token_and_superuser[0]}"}
            )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['username'] == mock_user.username

    async def test_get_user_detail_invalid_token(self, mocker):
        mock_user = User(
            username="superuser",
            email="test@mail.com",
            hashed_password="Password123!",
        )
        mock_user.id = 1
        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_user', return_value=mock_user)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                '/v1/api/users/1',
                headers={"Authorization": f"Bearer INVALID_TOKEN"}
            )
        assert response.status_code == 401

    async def test_update_user_not_found(self, mocker, get_access_token_and_superuser):
        mock_user = get_access_token_and_superuser[1]
        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_user', return_value=None)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                '/v1/api/users/999',
                headers={"Authorization": f"Bearer {get_access_token_and_superuser[0]}"}
            )
        assert response.status_code == 404
        assert response.json()['detail'] == 'Not found: User does not exist'

    # async def test_get_user_detail_forbidden_for_non_superuser(self, mocker, get_access_token_and_user):
    #     other_mock_user = User(
    #         username="user2",
    #         email="user2@mail.com",
    #         hashed_password="Password123!!",
    #     )
    #     other_mock_user.id = 2
    #     mocker.patch('auth.oauth2.get_user_by_token', return_value=get_access_token_and_user[1])
    #     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    #         response = await client.get(
    #             '/v1/api/users/2',
    #             headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"}
    #         )
    #     assert response.status_code == 403


@pytest.mark.asyncio
class TestPutUpdateUser:
    async def test_update_user_success(self, mocker, get_access_token_and_superuser):
        mock_user = get_access_token_and_superuser[1]
        mock_updated_user = User(
            id=1,
            username="updateduser",
            email="updateduser@mail.com",
            hashed_password="newpassword"
        )
        user_update = UserUpdate(
            username="updateduser",
            email="updateduser@mail.com",
            password="newpassword"
        )
        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_user', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.update_user', return_value=mock_updated_user)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                '/v1/api/users/1/update',
                headers={"Authorization": f"Bearer {get_access_token_and_superuser[0]}"},
                json=user_update.model_dump()
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['id'] == mock_updated_user.id
        assert response_data['username'] == mock_updated_user.username

    async def test_update_user_not_found(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]
        user_update = UserUpdate(
            username="updateduser",
            email="updateduser@mail.com",
            password="newpassword"
        )
        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_user', return_value=None)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                '/v1/api/users/999/update',
                headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"},
                json=user_update.model_dump()
            )
        assert response.status_code == 404
        assert response.json()['detail'] == 'Not found: User does not exist'

    # async def test_update_user_permission_denied(self, mocker, get_access_token_and_user):
    #     mock_user = get_access_token_and_user[1]
    #     user_update = UserUpdate(
    #         username="updateduser",
    #         email="updateduser@mail.com",
    #         password="newpassword"
    #     )
    #     mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
    #     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    #         response = await client.put(
    #             '/v1/api/users/1/update',
    #             headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"},
    #             json=user_update.model_dump()
    #         )
    #     assert response.status_code == 403
    #     assert response.json()['detail'] == "FORBIDDEN: Insufficient permissions for user ID=1"


@pytest.mark.asyncio
class TestDeleteUser:

    async def test_delete_user_success(self, mocker, get_access_token_and_superuser):
        mock_user = get_access_token_and_superuser[1]

        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_user', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.delete_user', return_value=mock_user)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                '/v1/api/users/1/delete',
                headers={"Authorization": f"Bearer {get_access_token_and_superuser[0]}"}
            )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['id'] == mock_user.id
        assert response_data['username'] == mock_user.username

    async def test_delete_user_not_found(self, mocker, get_access_token_and_superuser):
        mock_user = get_access_token_and_superuser[1]
        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_user', return_value=None)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                '/v1/api/users/999/delete',
                headers={"Authorization": f"Bearer {get_access_token_and_superuser[0]}"}
            )

        assert response.status_code == 404
        assert response.json()['detail'] == 'Not found: User does not exist'

    async def test_delete_user_permission_denied(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]

        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.user_crud.UserCrud.get_user', return_value=mock_user)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                '/v1/api/users/1/delete',
                headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"}
            )

        assert response.status_code == 403
        assert response.json()['detail'] == "FORBIDDEN: No permission to perform this action"
    #
    async def test_delete_user_unauthorized(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                '/v1/api/users/1/delete'
            )
        assert response.status_code == 401
        assert response.json()['detail'] == "Not authenticated"

    async def test_delete_user_invalid_token(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]
        mocker.patch('auth.oauth2.get_user_by_token', side_effect=Exception("Invalid token"))

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                '/v1/api/users/1/delete',
                headers={"Authorization": "Bearer invalid_token"}
            )
        assert response.status_code == 401




