import pytest
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import DBUser, RegisterUserRequest, Token, User
from auth.services import (
    authenticate_user,
    get_user_by_username,
    login_for_access_token,
    register_user,
)
from exceptions.exceptions import AuthenticationFailed, RegistrationFailed


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_duplicate_username(
    testing_data,
    testing_session,
) -> None:
    with pytest.raises(RegistrationFailed, match="Username has already been taken"):
        await register_user(
            RegisterUserRequest(
                username=testing_data["username"],
                email="new@email.com",
                password="new-pass",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_duplicate_email(
    testing_data,
    testing_session,
) -> None:
    with pytest.raises(RegistrationFailed, match="Email has already been taken"):
        await register_user(
            RegisterUserRequest(
                username="another-user",
                email=testing_data["email"],
                password="some_pass",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_duplicate_username_and_email(
    testing_data,
    testing_session,
) -> None:
    with pytest.raises(RegistrationFailed, match="Username has already been taken"):
        await register_user(
            RegisterUserRequest(
                username=testing_data["username"],
                email=testing_data["email"],
                password="some_pass",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_pseudo_username_race_condition(testing_session) -> None:
    # First registration should succeed
    await register_user(
        RegisterUserRequest(
            username="same-name", email="one@email.com", password="strongpassword"
        ),
        testing_session,
    )

    # Second registration should fail due to duplicate username
    with pytest.raises(RegistrationFailed):
        await register_user(
            RegisterUserRequest(
                username="same-name",
                email="another@email.com",
                password="strongerpassword",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_pseudo_email_race_condition(testing_session) -> None:
    # First registration should succeed
    await register_user(
        RegisterUserRequest(
            username="one-name", email="same@email.com", password="strongpassword"
        ),
        testing_session,
    )

    # Second registration should fail due to duplicate email
    with pytest.raises(RegistrationFailed):
        await register_user(
            RegisterUserRequest(
                username="another-name",
                email="same@email.com",
                password="strongerpassword",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_regular(
    testing_data, testing_session: AsyncSession
) -> None:
    test_user = RegisterUserRequest(**testing_data["register_payload"])
    results = await register_user(test_user, testing_session)

    # Check result contents
    assert isinstance(results, dict)
    assert results["detail"] == "Welcome to BuklatAPI, some-user!"

    # Check whether this new user exists in the database
    existing = (
        await testing_session.execute(
            select(DBUser).where(
                DBUser.username == testing_data["register_payload"]["username"]
            )
        )
    ).scalar_one_or_none()

    assert isinstance(existing, DBUser)
    assert existing.email == testing_data["register_payload"]["email"]


@pytest.mark.asyncio
async def test_get_user_by_username_returns_none_for_nonexistent_username(
    testing_session,
) -> None:
    user = await get_user_by_username("not-a-user", testing_session)

    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_username_regular(testing_data, testing_session) -> None:
    user = await get_user_by_username(testing_data["username"], testing_session)

    assert isinstance(user, DBUser)
    assert user.username == testing_data["username"]


@pytest.mark.asyncio
async def test_authenticate_user_returns_none_for_nonexistent_username(
    testing_session,
) -> None:
    authenticated = await authenticate_user(
        "not-a-username", SecretStr("some-pass"), testing_session
    )

    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_user_returns_none_for_incorrect_password(
    testing_data,
    testing_session,
) -> None:
    authenticated = await authenticate_user(
        testing_data["username"], SecretStr("incorrect-pass"), testing_session
    )

    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_user_regular(testing_data, testing_session) -> None:
    authenticated = await authenticate_user(
        testing_data["username"], testing_data["password"], testing_session
    )

    assert isinstance(authenticated, User)
    assert authenticated.username == testing_data["username"]
    assert authenticated.email == testing_data["email"]


@pytest.mark.asyncio
async def test_login_for_access_token_raises_AuthenticationFailed_for_nonexistent_username(
    testing_session,
) -> None:
    invalid_user_data = OAuth2PasswordRequestForm(
        username="not-a-user", password="not-a-pass"
    )

    with pytest.raises(AuthenticationFailed):
        await login_for_access_token(invalid_user_data, testing_session)


@pytest.mark.asyncio
async def test_login_for_access_token_raises_AuthenticationFailed_for_incorrect_password(
    testing_data,
    testing_session: AsyncSession,
) -> None:
    incorrect_password_data = OAuth2PasswordRequestForm(
        username=testing_data["username"], password="wrong-pw"
    )

    with pytest.raises(AuthenticationFailed):
        await login_for_access_token(incorrect_password_data, testing_session)


@pytest.mark.asyncio
async def test_login_for_access_token_regular(testing_data, testing_session) -> None:
    form_data = OAuth2PasswordRequestForm(
        username=testing_data["username"],
        password=testing_data["password"].get_secret_value(),
    )

    access_token = await login_for_access_token(form_data, testing_session)

    assert isinstance(access_token, Token)
    assert access_token.token_type == "bearer"
