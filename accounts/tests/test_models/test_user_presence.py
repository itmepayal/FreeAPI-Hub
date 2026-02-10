import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from accounts.models import UserPresence

User = get_user_model()

# ======================================================
# Fixtures
# ======================================================

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="presence@test.com",
        username="presenceuser",
        password="pass123"
    )


@pytest.fixture
def presence(user):
    return user.presence

# ======================================================
# Creation Tests
# ======================================================
@pytest.mark.django_db
def test_presence_created_and_linked(user, presence):
    assert presence.user == user
    assert presence.is_online is False
    assert presence.last_seen is None
    
# ======================================================
# mark_online Tests
# ======================================================
@pytest.mark.django_db
def test_mark_online_sets_fields(presence):
    presence.mark_online()
    presence.refresh_from_db()
    
    assert presence.is_online is True
    assert presence.last_seen is not None

# ======================================================
# mark_offline Tests
# ======================================================
@pytest.mark.django_db
def test_mark_offline_sets_fields(presence):
    presence.mark_online()
    presence.mark_offline()

    presence.refresh_from_db()
    
    assert presence.is_online is False
    assert presence.last_seen is not None

# ======================================================
# heartbeat Tests
# ======================================================

@pytest.mark.django_db
def test_heartbeat_updates_last_seen(presence):
    old = timezone.now() - timedelta(minutes=5)
    presence.last_seen = old
    presence.save()
    
    presence.heartbeat()
    presence.refresh_from_db()

    assert presence.last_seen > old


# ======================================================
# is_recently_active Tests
# ======================================================
@pytest.mark.django_db
def test_is_recently_active_true(presence):
    presence.last_seen = timezone.now()
    presence.save()

    assert presence.is_recently_active is True

@pytest.mark.django_db
def test_is_recently_active_false_when_old(presence):
    presence.last_seen = timezone.now() - timedelta(minutes=5)
    presence.save()
    
    assert presence.is_recently_active is False
    
@pytest.mark.django_db
def test_is_recently_active_false_when_none(presence):
    presence.last_seen = None
    presence.save()
    
    assert presence.is_recently_active is False
    
# ======================================================
# __str__ Test
# ======================================================
@pytest.mark.django_db
def test_str_representation(presence, user):
    s = str(presence)
    
    assert user.email in s
    assert "Presence<" in s

# ======================================================
# Default Test Message
# ======================================================
def test_default_status_message(presence):
    assert presence.status_message.startswith("Hey there")
    