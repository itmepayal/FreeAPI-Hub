import pytest
from datetime import timedelta

from django.db import IntegrityError
from django.utils import timezone
from freezegun import freeze_time

from accounts.models import UserPresence
from accounts.tests.factories.user_factory import UserFactory

@pytest.mark.django_db
class TestUserPresenceModel:
    """Unit tests for UserPresence model"""
    
    @pytest.fixture
    def user_presence(self):
        user = UserFactory()
        return user.presence
    
    # ------------------------------------------------------------------
    # BASIC MODEL BEHAVIOR
    # ------------------------------------------------------------------
    def test_user_presence_creation(self, user_presence):
        assert user_presence.user is not None
        assert user_presence.is_online is False
        assert user_presence.last_seen is None
        assert user_presence.status_message == "Hey there! I am using config Hub."
    
    def test_str_representation(self, user_presence):
        assert str(user_presence) == (
            f"Presence<{user_presence.user.email}:{user_presence.is_online}>"
        )
    
    # ------------------------------------------------------------------
    # ONLINE / OFFLINE STATE
    # ------------------------------------------------------------------
    @freeze_time("2024-01-01 12:00:00")
    def test_mark_online(self, user_presence):
        user_presence.mark_online()
        user_presence.refresh_from_db()

        assert user_presence.is_online is True
        assert user_presence.last_seen == timezone.now()
    
    @freeze_time("2024-01-01 12:00:00")
    def test_mark_offline(self, user_presence):
        user_presence.mark_online()
        user_presence.mark_offline()
        user_presence.refresh_from_db()

        assert user_presence.is_online is False
        assert user_presence.last_seen == timezone.now()

    # ------------------------------------------------------------------
    # HEARTBEAT
    # ------------------------------------------------------------------
    @freeze_time("2024-01-01 12:00:00")
    def test_heartbeat_updates_last_seen_only(self, user_presence):
        old_time = timezone.now() - timedelta(hours=1)
        original_status = user_presence.is_online
        
        user_presence.last_seen = old_time
        user_presence.save()
        
        user_presence.heartbeat()
        user_presence.refresh_from_db()
        
        assert user_presence.last_seen == timezone.now()
        assert user_presence.is_online == original_status
        
    # ------------------------------------------------------------------
    # RECENT ACTIVITY CHECK
    # ------------------------------------------------------------------
    def test_is_recently_active_true(self, user_presence):
        pass
    
     # ------------------------------------------------------------------
    # RECENT ACTIVITY CHECK
    # ------------------------------------------------------------------
    def test_is_recently_active_true(self, user_presence):
        user_presence.last_seen = timezone.now() - timedelta(seconds=60)
        user_presence.save()

        assert user_presence.is_recently_active is True

    def test_is_recently_active_false(self, user_presence):
        user_presence.last_seen = timezone.now() - timedelta(seconds=180)
        user_presence.save()

        assert user_presence.is_recently_active is False

    def test_is_recently_active_with_no_last_seen(self, user_presence):
        user_presence.last_seen = None
        user_presence.save()

        assert user_presence.is_recently_active is False

    # ------------------------------------------------------------------
    # ONE-TO-ONE RELATIONSHIP
    # ------------------------------------------------------------------
    def test_one_to_one_relationship_with_user(self):
        user = UserFactory()
        presence = UserPresence.objects.create(user=user)

        assert user.presence == presence

        # Ensure only one presence per user
        with pytest.raises(IntegrityError):
            UserPresence.objects.create(user=user)

    # ------------------------------------------------------------------
    # DATABASE INDEXES
    # ------------------------------------------------------------------
    def test_database_indexes(self):
        indexes = [index.fields for index in UserPresence._meta.indexes]

        assert ['is_online', 'last_seen'] in indexes