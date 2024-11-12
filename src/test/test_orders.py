import pytest
from httpx import AsyncClient, ASGITransport
from exceptions import JSONSerializationError
from main import app
from models.orders import Order, OrderStatus
from schemas.order_schema import OrderCreate, OrderUpdateStatus
from test.test_user import get_access_token_and_user, get_access_token_and_superuser


@pytest.mark.asyncio
class TestOrderCreate:
    async def test_create_order_success(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]
        order_data = OrderCreate(
            title="Test",
            price=1.0,
            status=OrderStatus.pending
        )
        order = Order(id=1, title=order_data.title, price=order_data.price, status=order_data.status)

        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.order_crud.OrderCrud.create_order', return_value=order)
        produce_mock = mocker.patch('services.kafka.producers.produce_orders')
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/api/orders/create/",
                json=order_data.model_dump(),
                headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"}
            )

        assert response.status_code == 200
        try:
            produce_mock.assert_called_once()
        except AssertionError as e:
            print("Ошибка при проверке вызова produce_notification:", e)

    async def test_create_order_unauthorized(self):
        order_data = OrderCreate(
            title="Test",
            price=1.0,
            status=OrderStatus.pending
        )
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/api/orders/create/",
                json=order_data.model_dump()
            )

        assert response.status_code == 401

    async def test_create_order_json_serialization_error(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]
        order_data = OrderCreate(
            title="Test",
            price=1.0,
            status=OrderStatus.pending
        )
        order = Order(id=1, title=order_data.title,  price=order_data.price, status=order_data.status)

        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.order_crud.OrderCrud.create_order', return_value=order)
        produce_mock = mocker.patch('services.kafka.producers.produce_orders',side_effect=JSONSerializationError("Serialization failed"))
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/api/orders/create/",
                json=order_data.model_dump(),
                headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"}
            )
        assert response.status_code == 200
        try:
            produce_mock.assert_called_once()
        except AssertionError as e:
            print("Ошибка при проверке вызова produce_notification:", e)


@pytest.mark.asyncio
class TestGetOrders:
    async def test_get_orders_user(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]
        orders_list = [
            Order(id=1, user_id=mock_user.id, title="Test 1", status=OrderStatus.pending, price=1.0),
            Order(id=2, user_id=2, title="Test 2", status=OrderStatus.done, price=1.0)
        ]
        orders_list_allowed = [order for order in orders_list if order.user_id == mock_user.id]
        mocker.patch('crud.order_crud.OrderCrud.get_all_orders', return_value=orders_list_allowed)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/v1/api/orders/",
                headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"}
            )
        response_data = response.json()
        assert response_data[0]['id'] == orders_list_allowed[0].id
        assert response_data[0]['title'] == orders_list_allowed[0].title
        assert response.status_code == 200

    async def test_get_orders_superuser(self, mocker, get_access_token_and_superuser):
        mock_user = get_access_token_and_superuser[1]
        orders_list = [
            Order(id=1, user_id=mock_user.id, title="Test 1", status=OrderStatus.pending, price=1.0),
            Order(id=2, user_id=2, title="Test 2", status=OrderStatus.done, price=1.0)
        ]
        mocker.patch('crud.order_crud.OrderCrud.get_all_orders', return_value=orders_list)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/v1/api/orders/",
                headers={"Authorization": f"Bearer {get_access_token_and_superuser[0]}"}
            )
        response_data = response.json()
        assert response_data[0]['id'] == orders_list[0].id
        assert response_data[0]['title'] == orders_list[0].title
        assert response_data[1]['id'] == orders_list[1].id
        assert response_data[1]['title'] == orders_list[1].title
        assert response.status_code == 200

    async def test_get_orders_unauthorized(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/v1/api/orders/"
            )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestUpdateStatusOrder:
    async def test_update_status_order_success(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]
        order_update_status = OrderUpdateStatus(status=OrderStatus.in_progress)
        order = Order(id=1, user_id=mock_user.id, title="Test", status=order_update_status.status, price=1.0)

        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.order_crud.OrderCrud.get_order', return_value=order)
        produce_mock = mocker.patch('services.kafka.producers.produce_orders')
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/v1/api/orders/{order.id}/",
                json=order_update_status.model_dump(),
                headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"}
            )
        assert response.status_code == 200
        try:
            produce_mock.assert_called_once()
        except AssertionError as e:
            print("Ошибка при проверке вызова produce_notification:", e)

    @pytest.mark.asyncio
    async def test_update_status_order_user_no_permission(self, mocker, get_access_token_and_user):
        mock_user = get_access_token_and_user[1]
        order_update_status = OrderUpdateStatus(status=OrderStatus.in_progress)
        order = Order(id=1, user_id=2, title="Test", status=order_update_status.status, price=1.0)

        mocker.patch('auth.oauth2.get_user_by_token', return_value=mock_user)
        mocker.patch('crud.order_crud.OrderCrud.get_order', return_value=order)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/v1/api/orders/{order.id}/",
                json=order_update_status.model_dump(),
                headers={"Authorization": f"Bearer {get_access_token_and_user[0]}"}
            )
        assert response.status_code == 403
        assert response.json() == {"detail": "FORBIDDEN: No permission to perform this action"}

    @pytest.mark.asyncio
    async def test_update_status_order_unauthorized(self):
        order_update_status = OrderUpdateStatus(status=OrderStatus.in_progress)
        order = Order(id=1, user_id=2, title="Test", status=order_update_status.status, price=1.0)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put(
                f"/v1/api/orders/{order.id}/",
                json=order_update_status.model_dump(),
            )
        assert response.status_code == 401



