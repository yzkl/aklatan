from datetime import datetime
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from auth.dependencies import get_current_active_user, get_current_user
from auth.models import User
from auth.utils import create_access_token
from exceptions.exceptions import InvalidAccountError, InvalidTokenError


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
@pytest.mark.asyncio
async def test_get_current_user_returns_InvalidTokenError_for_invalid_jwt(
    testing_session,
) -> None:
    invalid_token = "not-a-token"

    with pytest.raises(InvalidTokenError):
        await get_current_user(invalid_token, testing_session)


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
@pytest.mark.asyncio
async def test_get_current_user_returns_InvalidTokenError_for_expired_jwt(
    testing_data, testing_session
) -> None:
    expired_token = create_access_token(
        data=testing_data["register_payload"],
        now_fn=lambda: datetime(2000, 1, 1),
    )

    with pytest.raises(InvalidTokenError):
        await get_current_user(expired_token, testing_session)


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
@pytest.mark.asyncio
async def test_get_current_user_returns_InvalidTokenError_for_nonexistent_user(
    testing_data, testing_session
) -> None:
    invalid_user_token = create_access_token(
        {"sub": "not-a-user"},
    )

    with pytest.raises(InvalidTokenError, match="Invalid credentials"):
        await get_current_user(
            invalid_user_token,
            testing_session,
        )


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
@pytest.mark.asyncio
async def test_get_current_user_regular(testing_data, testing_session) -> None:
    token = create_access_token(
        testing_data["token_payload"],
    )

    user = await get_current_user(token, testing_session)

    assert isinstance(user, User)
    assert user.username == testing_data["username"]
    assert user.email == testing_data["email"]
    assert user.is_active


@pytest.mark.asyncio
async def test_get_current_active_user_raises_InvalidAccountError() -> None:
    # Create a deactivated user
    inactive_user = User(
        username="inactive-user", email="some@email.com", is_active=False
    )

    with pytest.raises(InvalidAccountError):
        await get_current_active_user(current_user=inactive_user)


@pytest.mark.asyncio
async def test_get_current_active_user_regular(testing_data) -> None:
    test_user = User(
        username=testing_data["username"],
        email=testing_data["email"],
        is_active=True,
    )

    active_user = await get_current_active_user(current_user=test_user)

    assert isinstance(active_user, User)
    assert active_user.username == testing_data["username"]
    assert active_user.email == testing_data["email"]
    assert active_user.is_active
