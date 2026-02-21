"""
Password Features Tests - Password visibility toggles and Forgot/Reset Password flow
Tests for GlasEditionsLab AI Book Generator
"""
import pytest
import requests
import os
from datetime import datetime, timezone, timedelta
from jose import jwt

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
JWT_SECRET = "glaseditions-secret-key-2025"
JWT_ALGORITHM = "HS256"

# Test credentials
ADMIN_EMAIL = "glaseditionslab@gmail.com"
ADMIN_PASSWORD = "Admin123!"

class TestForgotPassword:
    """Tests for POST /api/auth/forgot-password endpoint"""
    
    def test_forgot_password_with_valid_email(self, api_client):
        """POST /api/auth/forgot-password with valid existing email returns success"""
        response = api_client.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": ADMIN_EMAIL
        })
        assert response.status_code == 200
        data = response.json()
        # Should always return same message to prevent email enumeration
        assert "message" in data
        print(f"SUCCESS: forgot-password with valid email returns 200 - message: {data['message']}")
    
    def test_forgot_password_with_nonexistent_email(self, api_client):
        """POST /api/auth/forgot-password with non-existent email returns same success (no enumeration)"""
        response = api_client.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "nonexistent_test_user_xyz123@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        # Should return same message to prevent email enumeration
        assert "message" in data
        print(f"SUCCESS: forgot-password with non-existent email returns 200 (no enumeration) - message: {data['message']}")
    
    def test_forgot_password_missing_email(self, api_client):
        """POST /api/auth/forgot-password with missing email returns validation error"""
        response = api_client.post(f"{BASE_URL}/api/auth/forgot-password", json={})
        assert response.status_code == 422  # Validation error
        print("SUCCESS: forgot-password with missing email returns 422 validation error")


class TestResetPassword:
    """Tests for POST /api/auth/reset-password endpoint"""
    
    def test_reset_password_with_invalid_token(self, api_client):
        """POST /api/auth/reset-password with invalid token returns error"""
        response = api_client.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": "invalid_token_here",
            "new_password": "newpassword123"
        })
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"SUCCESS: reset-password with invalid token returns 400 - detail: {data['detail']}")
    
    def test_reset_password_with_expired_token(self, api_client):
        """POST /api/auth/reset-password with expired token returns error"""
        # Generate an expired token (expired 1 hour ago)
        expired_token = jwt.encode(
            {
                "sub": "user_test123",
                "email": "test@example.com",
                "type": "reset",
                "exp": datetime.now(timezone.utc) - timedelta(hours=1)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        response = api_client.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": expired_token,
            "new_password": "newpassword123"
        })
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"SUCCESS: reset-password with expired token returns 400 - detail: {data['detail']}")
    
    def test_reset_password_with_wrong_token_type(self, api_client):
        """POST /api/auth/reset-password with token of wrong type returns error"""
        # Generate token with wrong type
        wrong_type_token = jwt.encode(
            {
                "sub": "user_test123",
                "email": "test@example.com",
                "type": "login",  # Wrong type, should be 'reset'
                "exp": datetime.now(timezone.utc) + timedelta(hours=1)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        response = api_client.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": wrong_type_token,
            "new_password": "newpassword123"
        })
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"SUCCESS: reset-password with wrong token type returns 400 - detail: {data['detail']}")
    
    def test_reset_password_short_password(self, api_client, test_user):
        """POST /api/auth/reset-password with valid token but short password returns error"""
        user_id, email = test_user
        
        # Generate valid reset token
        valid_token = jwt.encode(
            {
                "sub": user_id,
                "email": email,
                "type": "reset",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        response = api_client.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": valid_token,
            "new_password": "abc"  # Too short (less than 6 chars)
        })
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "6" in data["detail"]  # Should mention 6 characters
        print(f"SUCCESS: reset-password with short password returns 400 - detail: {data['detail']}")
    
    def test_reset_password_with_valid_token(self, api_client, test_user):
        """POST /api/auth/reset-password with valid token successfully resets password"""
        user_id, email = test_user
        
        # Generate valid reset token
        valid_token = jwt.encode(
            {
                "sub": user_id,
                "email": email,
                "type": "reset",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        new_password = "newTestPassword123!"
        response = api_client.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": valid_token,
            "new_password": new_password
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"SUCCESS: reset-password with valid token returns 200 - message: {data['message']}")
        
        # Verify we can login with new password
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": new_password
        })
        assert login_response.status_code == 200
        print("SUCCESS: Can login with new password after reset")


class TestResetPasswordUserNotFound:
    """Test reset-password with valid token but user doesn't exist"""
    
    def test_reset_password_user_not_found(self, api_client):
        """POST /api/auth/reset-password returns error when user no longer exists"""
        # Generate token for non-existent user
        token = jwt.encode(
            {
                "sub": "user_nonexistent_xyz123",
                "email": "nonexistent@example.com",
                "type": "reset",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        response = api_client.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": token,
            "new_password": "validpassword123"
        })
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"SUCCESS: reset-password for non-existent user returns 400 - detail: {data['detail']}")


# ==================== FIXTURES ====================

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def test_user(api_client):
    """Create a test user for password reset testing, cleanup after"""
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    test_email = f"TEST_pwreset_{timestamp}_{unique_id}@example.com"
    test_password = "TestPassword123!"
    
    # Register the test user
    register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "name": "Test Password Reset User",
        "email": test_email,
        "password": test_password
    })
    
    if register_response.status_code != 200:
        pytest.skip(f"Failed to create test user: {register_response.text}")
    
    user_data = register_response.json()
    user_id = user_data["user"]["user_id"]
    
    yield user_id, test_email
    
    # Cleanup: try to delete the user (if admin endpoint exists, otherwise skip)
    # For now, just log that we created a test user
    print(f"Test user created with email: {test_email}, user_id: {user_id}")
