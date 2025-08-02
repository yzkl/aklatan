import pytest
from httpx import AsyncClient

from exceptions.exceptions import AuthenticationFailed, RegistrationFailed

URL_PREFIX = "/auth/"


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_duplicate_username(
    testing_data,
    async_client: AsyncClient,
) -> None:
    payload = testing_data["register_payload"].copy()
    payload["username"] = testing_data["username"]
    with pytest.raises(RegistrationFailed, match="Username has already been taken"):
        await async_client.post(URL_PREFIX, json=payload)


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_duplicate_email(
    testing_data,
    async_client: AsyncClient,
) -> None:
    payload = testing_data["register_payload"].copy()
    payload["email"] = testing_data["email"]
    with pytest.raises(RegistrationFailed, match="Email has already been taken"):
        await async_client.post(URL_PREFIX, json=payload)


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_username_race_condition_pseudo(
    testing_data,
    async_client: AsyncClient,
) -> None:
    payload1 = testing_data["register_payload"].copy()
    payload2 = payload1.copy()
    payload2["email"] = "another@email.com"  # Same username, different email

    # First registration attempt must succeed
    response = await async_client.post(URL_PREFIX, json=payload1)

    assert response.status_code == 200
    assert f"Welcome to BuklatAPI, {payload1['username']}" in response.text

    # Second registration must fail due to same username
    with pytest.raises(RegistrationFailed):
        response = await async_client.post(URL_PREFIX, json=payload2)


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_email_race_condition_pseudo(
    testing_data,
    async_client: AsyncClient,
) -> None:
    payload1 = testing_data["register_payload"].copy()
    payload2 = payload1.copy()
    payload2["username"] = "another-user"  # Different username, same email

    # First registration attempt must succeed
    response = await async_client.post(URL_PREFIX, json=payload1)

    assert response.status_code == 200
    assert f"Welcome to BuklatAPI, {payload1['username']}" in response.text

    # Second registration must fail due to same email
    with pytest.raises(RegistrationFailed):
        response = await async_client.post(URL_PREFIX, json=payload2)


@pytest.mark.asyncio
async def test_register_user_regular(testing_data, async_client: AsyncClient) -> None:
    response = await async_client.post(
        URL_PREFIX, json=testing_data["register_payload"]
    )

    assert response.status_code == 200
    assert (
        f"Welcome to BuklatAPI, {testing_data['register_payload']['username']}"
        in response.text
    )


@pytest.mark.asyncio
async def test_login_for_access_token_raises_AuthenticationFailed_for_invalid_username(
    async_client: AsyncClient,
) -> None:
    form_data = {"username": "not-a-user", "password": "somepass"}
    with pytest.raises(AuthenticationFailed):
        await async_client.post(
            URL_PREFIX + "token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )


@pytest.mark.asyncio
async def test_login_for_access_token_raises_AuthenticationFailed_for_incorrect_password(
    testing_data,
    async_client: AsyncClient,
) -> None:
    form_data = {"username": testing_data["username"], "password": "not-a-password"}
    with pytest.raises(AuthenticationFailed):
        await async_client.post(
            URL_PREFIX + "token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )


@pytest.mark.asyncio
async def test_login_for_access_token_regular(
    testing_data, async_client: AsyncClient
) -> None:
    form_data = {
        "username": testing_data["username"],
        "password": testing_data["password"].get_secret_value(),
    }
    response = await async_client.post(
        URL_PREFIX + "token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
