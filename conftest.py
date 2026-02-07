import pytest
from unittest.mock import Mock

from rest_framework.test import APIClient, APIRequestFactory

from accounts.tests.factories.user_factory import UserFactory


# =============================================================
# API Client Fixtures
# =============================================================

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, existing_user):
    api_client.force_authenticate(user=existing_user)
    return api_client


# =============================================================
# User Fixtures
# =============================================================

@pytest.fixture
def user_instance(db):
    return UserFactory(
        email="existing@example.com",
        username="existinguser",
        password="password123"
    )


@pytest.fixture
def existing_user(db):
    return UserFactory()


# =============================================================
# Data Fixtures
# =============================================================

@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
    }


@pytest.fixture
def valid_registration_data():
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "SecurePass123!",
    }


# =============================================================
# Mock Request Fixture
# =============================================================

@pytest.fixture
def mock_request():
    req = Mock()
    req.META = {"HTTP_X_FORWARDED_FOR": "192.168.1.1"}
    req.user = None
    return req


# =============================================================
# DRF Request Factory
# =============================================================

@pytest.fixture
def api_request():
    factory = APIRequestFactory()
    return factory.post(
        "/api/register/",
        {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123!"
        },
        format="json",
    )
