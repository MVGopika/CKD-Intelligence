from app.core import security
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_hash_and_verify_normal_password():
    password = "shortpass"
    hashed = security.hash_password(password)
    assert hashed != password
    assert security.verify_password(password, hashed)


def test_long_password_truncation():
    # construct a string longer than 72 bytes when encoded
    long_str = "x" * 100
    # hashing should not raise ValueError
    hashed = security.hash_password(long_str)
    assert security.verify_password(long_str, hashed)
    # truncated content should still verify
    truncated = long_str[:72]
    assert security.verify_password(truncated, hashed)


def test_verify_with_truncated_input():
    # make hash from truncated and verify with original long password
    long_str = "y" * 80
    truncated = long_str[:72]
    hashed = security.hash_password(truncated)
    assert security.verify_password(long_str, hashed)


def test_register_endpoint_rejects_long_password():
    payload = {
        "email": "longpass@example.com",
        "password": "z" * 80,
        "full_name": "Test Long",
        "role_name": "patient"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "Password too long" in response.json().get("detail", "")


def test_login_endpoint_rejects_long_password():
    payload = {"email": "doesnotmatter@example.com", "password": "p" * 80}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    # generic message
    assert "Invalid email" in response.json().get("detail", "")
