import pytest
from uuid import uuid4
from unittest.mock import Mock, MagicMock, patch
from django.db import DatabaseError, IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny

from accounts.models import User, UserSecurity, UserPresence
from accounts.services.auth.register_service import RegisterService
from accounts.views.auth import RegisterView
from core.exceptions import InternalServerException

# =============================================================
# RegisterService Tests
# =============================================================
class TestRegisterService:

    # ---------------------------------------------------------
    # SUCCESS FLOW
    # ---------------------------------------------------------
    @patch('accounts.services.auth.register_service.get_client_ip')
    @patch('accounts.services.auth.register_service.transaction')
    def test_successful_registration_flow(
        self, mock_transaction, mock_get_client_ip,
        valid_registration_data, mock_request
    ):
        # Arrange — mock IP + transaction
        mock_get_client_ip.return_value = "192.168.1.1"
        mock_transaction.atomic.return_value.__enter__.return_value = None
        mock_transaction.atomic.return_value.__exit__.return_value = None
        
        mock_on_commit = Mock()
        mock_transaction.on_commit = mock_on_commit
        
        # Arrange — mock user + token generation
        mock_user = Mock(email="newuser@example.com", username="newuser")
        mock_security = Mock()
        mock_security.generate_email_verification_token.return_value = "token"

        with patch.object(User.objects, 'create_user', return_value=mock_user), \
                patch.object(UserSecurity.objects, 'get_or_create', return_value=(mock_security, True)), \
                patch.object(UserPresence.objects, 'get_or_create', return_value=(Mock(), True)), \
                patch.object(RegisterService, 'logger') as mock_logger_method, \
                patch.object(RegisterService, 'send_verification_email') as mock_send:

            mock_logger = Mock()
            mock_logger_method.return_value = mock_logger

            # Act
            result = RegisterService.register_user(valid_registration_data, mock_request)

            # Assert — DB operations
            User.objects.create_user.assert_called_once()
            UserSecurity.objects.get_or_create.assert_called_once()
            UserPresence.objects.get_or_create.assert_called_once()

            # Assert — logging
            mock_logger.info.assert_called_once()

            # Assert — email scheduled post-commit
            callback = mock_on_commit.call_args.args[0]
            callback()
            mock_send.assert_called_once_with(mock_user, "token")

            assert result == mock_user


    # ---------------------------------------------------------
    # USER CREATION FAILURE
    # ---------------------------------------------------------
    @patch('accounts.services.auth.register_service.get_client_ip')
    @patch('accounts.services.auth.register_service.transaction')
    def test_registration_user_creation_failure(
        self, mock_transaction, mock_get_client_ip,
        valid_registration_data, mock_request
    ):
        mock_transaction.atomic.side_effect = Exception("DB fail")

        with patch.object(RegisterService, 'logger') as mock_logger_method:
            mock_logger_method.return_value = Mock()

            with pytest.raises(InternalServerException):
                RegisterService.register_user(valid_registration_data, mock_request)

            mock_logger_method.return_value.error.assert_called_once()


    # ---------------------------------------------------------
    # TOKEN GENERATION FAILURE
    # ---------------------------------------------------------
    @patch('accounts.services.auth.register_service.get_client_ip')
    @patch('accounts.services.auth.register_service.transaction')
    def test_token_generation_failure(
        self, mock_transaction, mock_get_client_ip,
        valid_registration_data, mock_request
    ):
        mock_transaction.atomic.return_value.__enter__.return_value = None
        mock_transaction.atomic.return_value.__exit__.return_value = None

        mock_user = Mock()
        mock_security = Mock()
        mock_security.generate_email_verification_token.side_effect = Exception()

        with patch.object(User.objects, 'create_user', return_value=mock_user), \
                patch.object(UserSecurity.objects, 'get_or_create', return_value=(mock_security, True)), \
                patch.object(RegisterService, 'logger') as mock_logger:

            mock_logger.return_value = Mock()

            with pytest.raises(InternalServerException):
                RegisterService.register_user(valid_registration_data, mock_request)

            mock_logger.return_value.error.assert_called_once()


    # ---------------------------------------------------------
    # EMAIL SEND SUCCESS
    # ---------------------------------------------------------
    @patch('accounts.services.auth.register_service.send_email')
    @patch.object(RegisterService, 'logger')
    def test_send_verification_email(self, mock_logger_method, mock_send_email):

        mock_logger = Mock()
        mock_logger_method.return_value = mock_logger

        user = Mock(email="a@test.com", username="abc", id="1")

        with patch('accounts.services.auth.register_service.settings') as mock_settings:
            mock_settings.FRONTEND_URL = "http://front"
            mock_settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID = "tpl"

            RegisterService.send_verification_email(user, "rawtoken")

        mock_send_email.assert_called_once_with(
            to_email="a@test.com",
            template_id="tpl",
            dynamic_data={
                "username": "abc",
                "verify_link": "http://front/verify-email/rawtoken",
            },
        )

        mock_logger.info.assert_called_once()

    # ---------------------------------------------------------
    # DUPLICATE EMAIL
    # ---------------------------------------------------------
    
    @patch('accounts.services.auth.register_service.get_client_ip')
    def test_registration_duplicate_email(
        self, mock_get_client_ip, valid_registration_data, mock_request
    ):
        mock_get_client_ip.return_value = "1.1.1.1"

        with patch.object(User.objects, "create_user", 
                            side_effect=IntegrityError("dup")), \
                        patch.object(RegisterService, "logger") as mock_logger:
                            
                            with pytest.raises(InternalServerException):
                                RegisterService.register_user(valid_registration_data, mock_request)
                                
                            mock_logger().error.assert_called_once()
                            
    # ---------------------------------------------------------
    # EMPTY DATA
    # ---------------------------------------------------------
    @patch('accounts.services.auth.register_service.get_client_ip')
    def test_registration_empty_data(self, mock_get_client_ip, mock_request):
        mock_get_client_ip.return_value = "1.1.1.1"
        with patch.object(User.objects, "create_user", side_effect=ValidationError("bad")), \
            patch.object(RegisterService, "logger") as mock_logger:
                with pytest.raises(InternalServerException):
                    RegisterService.register_user({}, mock_request)
                    
                mock_logger().error.assert_called_once()
    
    # ---------------------------------------------------------
    # IP LOGGING
    # ---------------------------------------------------------
    @patch('accounts.services.auth.register_service.get_client_ip')
    @patch('accounts.services.auth.register_service.transaction')
    def test_registration_ip_logging(
        self, mock_transaction, mock_get_client_ip,
        valid_registration_data, mock_request
    ):
        test_ip = "203.0.113.1"
        mock_get_client_ip.return_value = test_ip
        
        
        mock_atomic = MagicMock()
        mock_atomic.__enter__.return_value = None
        mock_atomic.__exit__.return_value = None
        
        mock_transaction.atomic.return_value = mock_atomic
        mock_transaction.on_commit = Mock()
        
        mock_security = Mock()
        mock_security.generate_email_verification_token.return_value = "tok"
        
        with patch.object(User.objects, "create_user", return_value=Mock()), \
            patch.object(UserSecurity.objects, "get_or_create", return_value=(mock_security, True)), \
            patch.object(UserPresence.objects, "get_or_create", return_value=(Mock(), True)), \
            patch.object(RegisterService, "logger") as mock_logger, \
            patch.object(RegisterService, "send_verification_email"):
                
                RegisterService.register_user(valid_registration_data, mock_request)
                
                extra = mock_logger().info.call_args.kwargs["extra"]
                assert extra["ip"] == test_ip
    # ---------------------------------------------------------
    # TRANSACTION ROLLBACK
    # ---------------------------------------------------------
    @patch('accounts.services.auth.register_service.get_client_ip')
    @patch('accounts.services.auth.register_service.transaction')
    def test_atomic_transaction_rollback_on_failure(
        self, mock_transaction, mock_get_client_ip,
        valid_registration_data, mock_request
    ):  
        mock_get_client_ip.return_value = "1.1.1.1"
        
        mock_atomic = MagicMock()
        mock_atomic.__enter__.return_value = None
        mock_atomic.__exit__.side_effect = IntegrityError("rollback")
        mock_transaction.atomic.return_value = mock_atomic

        with patch.object(User.objects, "create_user",
                            side_effect=IntegrityError("fail")), \
                patch.object(RegisterService, "logger"):
                
                with pytest.raises(InternalServerException):
                    RegisterService.register_user(valid_registration_data, mock_request)

                assert mock_atomic.__enter__.called
                assert mock_atomic.__exit__.called
                
# =============================================================
# EMAIL SENDER TESTS
# =============================================================
class TestSendVerificationEmail:
    def test_send_verification_email_success(self):
        mock_user = Mock(
            id="123",
            email="test@example.com",
            username="tester"
        )
        with patch('accounts.services.auth.register_service.settings') as mock_settings, \
                patch('accounts.services.auth.register_service.send_email') as mock_send, \
                patch.object(RegisterService, "logger") as mock_logger:
                        mock_settings.FRONTEND_URL = "https://app.test"
                        mock_settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID = "tpl-1"
                        
                        RegisterService.send_verification_email(mock_user, "tok123")
                        
                        mock_send.assert_called_once_with(
                            to_email="test@example.com",
                            template_id="tpl-1",
                            dynamic_data={
                                "username": "tester",
                                "verify_link": "https://app.test/verify-email/tok123",
                            },
                        )
                        
                        mock_logger().info.assert_called_once()
    
    def test_send_verification_email_failure_logs(self):
        mock_user = Mock(id="123", email="x@test.com", username="x")
        with patch('accounts.services.auth.register_service.settings') as mock_settings, \
                patch('accounts.services.auth.register_service.send_email',
                    side_effect=Exception("email fail")), \
                patch.object(RegisterService, "logger") as mock_logger:
                    
                    mock_settings.FRONTEND_URL = "https://app.test"
                    mock_settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID = "tpl"
                    
                    with pytest.raises(Exception):
                        RegisterService.send_verification_email(mock_user, "tok")

                    mock_logger().info.assert_not_called()
                    
                    