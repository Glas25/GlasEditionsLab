"""
GlasEditionsLab - Account Page & Chapter Editing Tests
Tests for: Password Change, Subscription Details, Chapter Inline Editing
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin test credentials
ADMIN_EMAIL = "glaseditionslab@gmail.com"
ADMIN_PASSWORD = "Admin123!"

# Test state
test_state = {
    "admin_token": None,
    "regular_user_token": None,
    "regular_user_email": f"test.account.{int(time.time())}@example.com",
    "regular_user_password": "TestPassword123!",
    "existing_book_id": "77576020-db4e-486e-9c05-c06d0ae3da8c"
}


class TestAdminLogin:
    """Admin user login for subsequent tests"""
    
    def test_admin_login(self):
        """Test admin user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        
        assert "access_token" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["subscription"] == "admin"
        
        test_state["admin_token"] = data["access_token"]
        print(f"✓ Admin logged in: {ADMIN_EMAIL}")


class TestAccountSubscriptionEndpoint:
    """Tests for GET /api/account/subscription"""
    
    def test_admin_subscription_details(self):
        """Test that admin user gets correct subscription info"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        response = requests.get(f"{BASE_URL}/api/account/subscription", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify admin-specific fields
        assert data["is_active"] == True, "Admin should have active subscription"
        assert data["is_admin"] == True, "Admin flag should be True"
        assert data["subscription"] == "admin", "Subscription should be 'admin'"
        assert data["can_cancel"] == False, "Admin cannot cancel subscription"
        assert data["days_remaining"] == -1, "Admin has unlimited (-1) days"
        
        # Verify plan details
        assert data["plan_details"] is not None, "Admin should have plan details"
        assert data["plan_details"]["name"] == "Administrateur"
        assert data["plan_details"]["price"] == 0
        assert data["plan_details"]["books_per_month"] == -1  # Unlimited
        assert data["plan_details"]["max_chapters"] == -1  # Unlimited
        assert data["plan_details"]["cover_generation"] == True
        
        print(f"✓ Admin subscription endpoint returns correct data")
    
    def test_subscription_requires_auth(self):
        """Test subscription endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/account/subscription")
        assert response.status_code == 401
        assert "Non authentifié" in response.json()["detail"]
        print("✓ Subscription endpoint correctly requires auth")


class TestPasswordChange:
    """Tests for POST /api/account/change-password"""
    
    def test_password_change_with_correct_password(self):
        """Test password change with correct current password -> success"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        response = requests.post(f"{BASE_URL}/api/account/change-password", headers=headers, json={
            "current_password": ADMIN_PASSWORD,
            "new_password": ADMIN_PASSWORD  # Same password (allowed)
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Mot de passe modifié avec succès"
        print("✓ Password change with correct password: SUCCESS")
    
    def test_password_change_with_wrong_password(self):
        """Test password change with wrong current password -> error"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        response = requests.post(f"{BASE_URL}/api/account/change-password", headers=headers, json={
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword456!"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Mot de passe actuel incorrect"
        print("✓ Password change with wrong password: CORRECT ERROR")
    
    def test_password_change_too_short(self):
        """Test password change with new password too short"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        response = requests.post(f"{BASE_URL}/api/account/change-password", headers=headers, json={
            "current_password": ADMIN_PASSWORD,
            "new_password": "12345"  # Less than 6 chars
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "6 caractères" in data["detail"]
        print("✓ Password too short correctly rejected")
    
    def test_password_change_requires_auth(self):
        """Test password change requires authentication"""
        response = requests.post(f"{BASE_URL}/api/account/change-password", json={
            "current_password": "test",
            "new_password": "test123"
        })
        assert response.status_code == 401
        print("✓ Password change correctly requires auth")


class TestChapterEditing:
    """Tests for PUT /api/books/{book_id}/chapters/{chapter_num}"""
    
    def test_edit_chapter_content(self):
        """Test editing chapter content persists correctly"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        book_id = test_state["existing_book_id"]
        
        # Edit chapter 1 with new content
        test_content = f"Edited chapter content for testing - {int(time.time())}"
        response = requests.put(f"{BASE_URL}/api/books/{book_id}/chapters/1", headers=headers, json={
            "content": test_content
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response contains updated book
        assert data["id"] == book_id
        assert len(data["outline"]) > 0
        
        chapter1 = data["outline"][0]
        assert chapter1["content"] == test_content, "Content should be updated"
        assert chapter1["edited_manually"] == True, "edited_manually flag should be True"
        assert chapter1["status"] == "completed", "Status should be completed"
        assert chapter1["word_count"] > 0, "Word count should be calculated"
        
        print(f"✓ Chapter edit: Content saved with edited_manually=True")
    
    def test_edit_chapter_persistence(self):
        """Test that edited chapter content persists in DB"""
        book_id = test_state["existing_book_id"]
        
        # Fetch book to verify persistence
        response = requests.get(f"{BASE_URL}/api/books/{book_id}")
        assert response.status_code == 200
        data = response.json()
        
        chapter1 = data["outline"][0]
        assert chapter1["edited_manually"] == True, "edited_manually should persist"
        print("✓ Chapter edit: Changes persisted in database")
    
    def test_edit_chapter_invalid_number(self):
        """Test editing invalid chapter number returns error"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        book_id = test_state["existing_book_id"]
        
        # Try to edit chapter 999 (invalid)
        response = requests.put(f"{BASE_URL}/api/books/{book_id}/chapters/999", headers=headers, json={
            "content": "Invalid chapter"
        })
        
        assert response.status_code == 400
        assert "invalide" in response.json()["detail"].lower()
        print("✓ Invalid chapter number correctly rejected")
    
    def test_edit_chapter_requires_auth(self):
        """Test chapter editing requires authentication"""
        book_id = test_state["existing_book_id"]
        response = requests.put(f"{BASE_URL}/api/books/{book_id}/chapters/1", json={
            "content": "Unauthorized edit"
        })
        assert response.status_code == 401
        print("✓ Chapter edit correctly requires auth")
    
    def test_edit_chapter_nonexistent_book(self):
        """Test editing chapter of non-existent book"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        response = requests.put(f"{BASE_URL}/api/books/nonexistent-book-id/chapters/1", headers=headers, json={
            "content": "Test"
        })
        assert response.status_code == 404
        print("✓ Non-existent book correctly returns 404")


class TestBookListAuth:
    """Tests for GET /api/books authentication"""
    
    def test_book_list_requires_auth(self):
        """Test that GET /api/books requires authentication"""
        response = requests.get(f"{BASE_URL}/api/books")
        assert response.status_code == 401
        data = response.json()
        assert "connecté" in data["detail"].lower() or "authentifié" in data["detail"].lower()
        print("✓ Book list correctly requires authentication")
    
    def test_book_list_returns_user_books(self):
        """Test that GET /api/books returns only user's books"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        response = requests.get(f"{BASE_URL}/api/books", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Book list returns {len(data)} books for authenticated user")


class TestCancelSubscriptionErrors:
    """Tests for subscription cancel/reactivate error cases"""
    
    def test_admin_cannot_cancel(self):
        """Test that admin accounts cannot cancel subscription"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        response = requests.post(f"{BASE_URL}/api/account/cancel-subscription", headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "admin" in data["detail"].lower()
        print("✓ Admin correctly cannot cancel subscription")
    
    def test_reactivate_without_subscription(self):
        """Test reactivate fails without stripe subscription"""
        headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
        response = requests.post(f"{BASE_URL}/api/account/reactivate-subscription", headers=headers)
        
        # Admin doesn't have stripe_subscription_id, so should fail
        assert response.status_code == 400
        print("✓ Reactivate correctly fails without stripe subscription")


class TestRegularUserPasswordFlow:
    """Test password change flow for regular user (not Google-only)"""
    
    def test_register_regular_user(self):
        """Register a regular user for password tests"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_state["regular_user_email"],
            "password": test_state["regular_user_password"],
            "name": "Test Account User"
        })
        
        assert response.status_code == 200
        data = response.json()
        test_state["regular_user_token"] = data["access_token"]
        print(f"✓ Regular user registered: {test_state['regular_user_email']}")
    
    def test_regular_user_password_change(self):
        """Test password change for regular user"""
        headers = {"Authorization": f"Bearer {test_state['regular_user_token']}"}
        
        # Change password
        new_password = "NewTestPassword456!"
        response = requests.post(f"{BASE_URL}/api/account/change-password", headers=headers, json={
            "current_password": test_state["regular_user_password"],
            "new_password": new_password
        })
        
        assert response.status_code == 200
        print("✓ Regular user password change: SUCCESS")
        
        # Verify can login with new password
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_state["regular_user_email"],
            "password": new_password
        })
        assert response.status_code == 200
        print("✓ Login with new password: SUCCESS")


# Cleanup
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    """Cleanup test data after all tests"""
    yield
    # Cleanup test users
    import subprocess
    cmd = f'''mongosh --quiet --eval "
        use('test_database');
        db.users.deleteMany({{'email': /test\\.account\\./}});
        print('Account test cleanup completed');
    "'''
    subprocess.run(cmd, shell=True, capture_output=True)
    print("\n✓ Test cleanup completed")
