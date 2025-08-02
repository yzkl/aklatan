from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from bcrypt import checkpw
from pydantic import SecretStr

from auth.models import TokenData
from auth.utils import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from exceptions.exceptions import InvalidTokenError


def test_get_password_hash_returns_valid_hash(testing_data) -> None:
    hashed_password = get_password_hash(testing_data["password"])

    assert isinstance(hashed_password, str)
    assert hashed_password != testing_data["password"]
    assert checkpw(
        testing_data["password"].get_secret_value().encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def test_get_password_hash_randomness(testing_data) -> None:
    hash1 = get_password_hash(testing_data["password"])
    hash2 = get_password_hash(testing_data["password"])

    assert hash1 != hash2


def test_verify_password_returns_true(testing_data) -> None:
    hashed_password = get_password_hash(testing_data["password"])

    assert verify_password(testing_data["password"], hashed_password)


def test_verify_password_returns_false_for_incorrect_password(testing_data) -> None:
    hashed_password = get_password_hash(testing_data["password"])
    wrong_password = SecretStr("open_sesame")

    assert not verify_password(wrong_password, hashed_password)


def test_verify_password_returns_false_for_invalid_hash(testing_data) -> None:
    invalid_hash = "not_a_bcrypt_hash"

    assert not verify_password(testing_data["password"], invalid_hash)


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
def test_create_access_token_returns_decodable_jwt(testing_data) -> None:
    token = create_access_token(
        testing_data["token_payload"],
    )
    decoded = jwt.decode(
        token,
        testing_data["secret_key"].get_secret_value(),
        [testing_data["algorithm"].get_secret_value()],
    )

    assert decoded["sub"] == "test-user"
    assert "exp" in decoded


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
def test_create_access_token_w_default_expiration(testing_data) -> None:
    token = create_access_token(testing_data["token_payload"])
    decoded = jwt.decode(
        token,
        testing_data["secret_key"].get_secret_value(),
        [testing_data["algorithm"].get_secret_value()],
    )

    assert decoded["exp"] == int(
        (datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()
    )


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
def test_create_access_token_w_custom_expiration(testing_data) -> None:
    token = create_access_token(
        testing_data["token_payload"],
        expires_delta=timedelta(minutes=45),
    )
    decoded = jwt.decode(
        token,
        testing_data["secret_key"].get_secret_value(),
        [testing_data["algorithm"].get_secret_value()],
    )

    assert decoded["exp"] == int(
        (datetime.now(timezone.utc) + timedelta(minutes=45)).timestamp()
    )


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
def test_create_access_token_preserves_payload(testing_data) -> None:
    testing_data["token_payload"].update({"role": "admin"})
    token = create_access_token(
        testing_data["token_payload"],
        expires_delta=timedelta(minutes=45),
    )
    decoded = jwt.decode(
        token,
        testing_data["secret_key"].get_secret_value(),
        [testing_data["algorithm"].get_secret_value()],
    )

    for key in testing_data["token_payload"]:
        assert decoded[key] == testing_data["token_payload"][key]


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
def test_verify_token_raises_InvalidTokenError_for_invalid_token(testing_data) -> None:
    invalid_token = "not_a_token"

    with pytest.raises(InvalidTokenError):
        verify_token(invalid_token)


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
def test_verify_token_raises_InvalidTokenError_for_expired_token(testing_data) -> None:
    expired_token = create_access_token(
        data=testing_data["token_payload"],
        now_fn=lambda: datetime(2025, 1, 1),
    )

    with pytest.raises(InvalidTokenError):
        verify_token(expired_token)


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
def test_verify_token_raises_InvalidTokenError_for_missing_sub_claim(
    testing_data,
) -> None:
    test_load = {"role": "admin"}
    missing_claim_token = create_access_token(
        test_load,
    )

    with pytest.raises(InvalidTokenError):
        verify_token(missing_claim_token)


@patch("auth.utils.SECRET_KEY", new=SecretStr("strongkey"))
@patch("auth.utils.ALGORITHM", new=SecretStr("HS256"))
def test_verify_token_regular(testing_data) -> None:
    token = create_access_token(
        testing_data["token_payload"],
    )

    verified = verify_token(token)

    assert isinstance(verified, TokenData)
    assert verified.username == "test-user"
