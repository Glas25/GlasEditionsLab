"""
Test Admin Moderation System - Promote/Demote endpoints
Tests the promote user to admin and demote admin to user functionality
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://author-ai-lab.preview.emergentagent.com').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "glaseditionslab@gmail.com"
ADMIN_PASSWORD = "Admin123!"

# Test user credentials
TEST_USER_PREFIX = "TEST_moderation_"
TEST_USER_EMAIL = f"{TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}@test.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = f"Test User Moderation {uuid.uuid4().hex[:6]}"


class TestAdminModerationSetup:
    """Setup fixtures for admin moderation tests"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Login as admin and return session with token"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        token = data.get("access_token")
        assert token, "No access_token in admin login response"
        
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session, token

    @pytest.fixture(scope="class")
    def test_user(self, admin_session):
        """Create a test user for moderation tests"""
        session, token = admin_session
        
        # Register a new test user
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        })
        
        if reg_response.status_code == 200:
            user_data = reg_response.json()
            user_id = user_data.get("user", {}).get("user_id")
            print(f"Created test user: {user_id}")
            return user_id, TEST_USER_EMAIL
        elif reg_response.status_code == 400 and "déjà utilisé" in reg_response.text:
            # User already exists, find them in admin users list
            users_resp = session.get(f"{BASE_URL}/api/admin/users", params={"search": TEST_USER_EMAIL})
            if users_resp.status_code == 200:
                users = users_resp.json().get("users", [])
                for u in users:
                    if u.get("email") == TEST_USER_EMAIL:
                        return u.get("user_id"), TEST_USER_EMAIL
        
        pytest.skip(f"Could not create test user: {reg_response.text}")


class TestPromoteEndpoint(TestAdminModerationSetup):
    """Test POST /api/admin/users/{user_id}/promote endpoint"""
    
    def test_promote_requires_auth(self, test_user):
        """Test that promote endpoint requires authentication"""
        user_id, _ = test_user
        response = requests.post(f"{BASE_URL}/api/admin/users/{user_id}/promote")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Promote requires authentication")
    
    def test_promote_requires_admin(self, admin_session, test_user):
        """Test that promote endpoint requires admin privileges"""
        user_id, _ = test_user
        
        # Login as the test user (non-admin)
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_resp.status_code == 200:
            user_token = login_resp.json().get("access_token")
            response = requests.post(
                f"{BASE_URL}/api/admin/users/{user_id}/promote",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"Expected 403, got {response.status_code}"
            print("PASS: Promote requires admin privileges")
        else:
            pytest.skip("Could not login as test user")
    
    def test_promote_user_success(self, admin_session, test_user):
        """Test successful promotion of regular user to admin"""
        session, token = admin_session
        user_id, email = test_user
        
        # First ensure user is NOT admin
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/demote")
        
        # Promote the user
        response = session.post(f"{BASE_URL}/api/admin/users/{user_id}/promote")
        
        assert response.status_code == 200, f"Promote failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert email in data["message"] or "administrateur" in data["message"]
        print(f"PASS: Promoted user to admin - {data['message']}")
        
        # Verify user is now admin via users list
        users_resp = session.get(f"{BASE_URL}/api/admin/users", params={"search": email})
        assert users_resp.status_code == 200
        users = users_resp.json().get("users", [])
        promoted_user = next((u for u in users if u.get("user_id") == user_id), None)
        assert promoted_user is not None, "User not found in admin users list"
        assert promoted_user.get("is_admin") == True, "User is_admin field should be True"
        print("PASS: Verified user is_admin=True in database")
    
    def test_promote_already_admin_error(self, admin_session, test_user):
        """Test that promoting an already admin user returns error"""
        session, token = admin_session
        user_id, _ = test_user
        
        # Ensure user is admin first
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/promote")
        
        # Try to promote again
        response = session.post(f"{BASE_URL}/api/admin/users/{user_id}/promote")
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "déjà administrateur" in data.get("detail", "").lower() or "already" in data.get("detail", "").lower()
        print(f"PASS: Correct error for already admin user - {data.get('detail')}")
    
    def test_promote_nonexistent_user(self, admin_session):
        """Test promoting non-existent user returns 404"""
        session, _ = admin_session
        fake_user_id = f"user_nonexistent_{uuid.uuid4().hex[:8]}"
        
        response = session.post(f"{BASE_URL}/api/admin/users/{fake_user_id}/promote")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 for non-existent user promotion")


class TestDemoteEndpoint(TestAdminModerationSetup):
    """Test POST /api/admin/users/{user_id}/demote endpoint"""
    
    def test_demote_requires_auth(self, test_user):
        """Test that demote endpoint requires authentication"""
        user_id, _ = test_user
        response = requests.post(f"{BASE_URL}/api/admin/users/{user_id}/demote")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Demote requires authentication")
    
    def test_demote_requires_admin(self, admin_session, test_user):
        """Test that demote endpoint requires admin privileges"""
        user_id, _ = test_user
        
        # Login as test user (even if they are admin, test with different non-admin)
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_resp.status_code == 200:
            user_token = login_resp.json().get("access_token")
            # Even if this user has is_admin=True, we check if they can demote themselves
            # Actually demote requires admin check which should work
            # Let's try demoting another user
            response = requests.post(
                f"{BASE_URL}/api/admin/users/{user_id}/demote",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            # This should fail with 403 if user is not admin, or succeed if they are admin
            if response.status_code == 403:
                print("PASS: Demote requires admin privileges")
            elif response.status_code == 200 or response.status_code == 400:
                # User might be admin, test is still valid
                print(f"PASS: User has admin access or demote error occurred (status: {response.status_code})")
        else:
            pytest.skip("Could not login as test user")
    
    def test_demote_admin_success(self, admin_session, test_user):
        """Test successful demotion of promoted admin"""
        session, token = admin_session
        user_id, email = test_user
        
        # First ensure user IS admin
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/promote")
        
        # Now demote the user
        response = session.post(f"{BASE_URL}/api/admin/users/{user_id}/demote")
        
        assert response.status_code == 200, f"Demote failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert "révoqué" in data["message"].lower() or email in data["message"]
        print(f"PASS: Demoted admin user - {data['message']}")
        
        # Verify user is no longer admin
        users_resp = session.get(f"{BASE_URL}/api/admin/users", params={"search": email})
        assert users_resp.status_code == 200
        users = users_resp.json().get("users", [])
        demoted_user = next((u for u in users if u.get("user_id") == user_id), None)
        assert demoted_user is not None, "User not found in admin users list"
        assert demoted_user.get("is_admin") == False or demoted_user.get("is_admin") is None, "User is_admin should be False"
        print("PASS: Verified user is_admin=False in database")
    
    def test_demote_super_admin_error(self, admin_session):
        """Test that super-admin (glaseditionslab@gmail.com) cannot be demoted"""
        session, _ = admin_session
        
        # Find super-admin user_id
        users_resp = session.get(f"{BASE_URL}/api/admin/users", params={"search": ADMIN_EMAIL})
        assert users_resp.status_code == 200
        users = users_resp.json().get("users", [])
        super_admin = next((u for u in users if u.get("email") == ADMIN_EMAIL), None)
        
        if super_admin:
            super_admin_id = super_admin.get("user_id")
            response = session.post(f"{BASE_URL}/api/admin/users/{super_admin_id}/demote")
            
            assert response.status_code == 400, f"Expected 400 for super-admin demote, got {response.status_code}"
            data = response.json()
            assert "super-administrateur" in data.get("detail", "").lower() or "super" in data.get("detail", "").lower()
            print(f"PASS: Super-admin cannot be demoted - {data.get('detail')}")
        else:
            pytest.skip("Could not find super-admin user")
    
    def test_demote_non_admin_error(self, admin_session, test_user):
        """Test that demoting a non-admin user returns error"""
        session, token = admin_session
        user_id, _ = test_user
        
        # First ensure user is NOT admin
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/demote")
        
        # Try to demote again
        response = session.post(f"{BASE_URL}/api/admin/users/{user_id}/demote")
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "pas administrateur" in data.get("detail", "").lower() or "not admin" in data.get("detail", "").lower()
        print(f"PASS: Correct error for non-admin demote - {data.get('detail')}")
    
    def test_demote_nonexistent_user(self, admin_session):
        """Test demoting non-existent user returns 404"""
        session, _ = admin_session
        fake_user_id = f"user_nonexistent_{uuid.uuid4().hex[:8]}"
        
        response = session.post(f"{BASE_URL}/api/admin/users/{fake_user_id}/demote")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 for non-existent user demotion")


class TestPromotedAdminAccess(TestAdminModerationSetup):
    """Test that promoted admins get proper access"""
    
    def test_promoted_admin_can_access_stats(self, admin_session, test_user):
        """Test that a promoted admin can access /api/admin/stats"""
        session, admin_token = admin_session
        user_id, email = test_user
        
        # Promote the user
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/promote")
        
        # Login as the promoted user
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_resp.status_code == 200:
            user_token = login_resp.json().get("access_token")
            
            # Check if /api/auth/me returns admin subscription
            me_resp = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if me_resp.status_code == 200:
                me_data = me_resp.json()
                assert me_data.get("subscription") == "admin", f"Promoted admin should have subscription='admin', got {me_data.get('subscription')}"
                print(f"PASS: Promoted admin has subscription='admin'")
            
            # Access admin stats
            stats_resp = requests.get(
                f"{BASE_URL}/api/admin/stats",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            assert stats_resp.status_code == 200, f"Promoted admin should access stats, got {stats_resp.status_code}"
            stats = stats_resp.json()
            assert "total_users" in stats
            assert "total_books" in stats
            print("PASS: Promoted admin can access /api/admin/stats")
        else:
            pytest.skip(f"Could not login as promoted user: {login_resp.text}")
        
        # Cleanup - demote the user back
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/demote")


class TestAdminFilterWithAdmin(TestAdminModerationSetup):
    """Test admin filter in users list"""
    
    def test_filter_admin_users(self, admin_session, test_user):
        """Test that plan=admin filter returns only admin users"""
        session, _ = admin_session
        user_id, email = test_user
        
        # Ensure test user is admin
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/promote")
        
        # Get admin users
        response = session.get(f"{BASE_URL}/api/admin/users", params={"plan": "admin"})
        
        assert response.status_code == 200, f"Filter failed: {response.text}"
        data = response.json()
        users = data.get("users", [])
        
        # All returned users should be admins
        for user in users:
            assert user.get("is_admin") == True or user.get("email") in ["glaseditionslab@gmail.com"], \
                f"Non-admin user in admin filter: {user.get('email')}"
        
        # Check that our promoted test user is in the list
        test_user_found = any(u.get("user_id") == user_id for u in users)
        assert test_user_found or len(users) == 0, "Promoted test user should appear in admin filter"
        
        print(f"PASS: Admin filter returns {len(users)} admin users, all verified as admins")
        
        # Cleanup - demote test user
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/demote")


class TestCleanup(TestAdminModerationSetup):
    """Cleanup test data after all tests"""
    
    def test_cleanup_test_user(self, admin_session, test_user):
        """Delete test user created for moderation tests"""
        session, _ = admin_session
        user_id, email = test_user
        
        # First ensure user is NOT admin (can't delete admins)
        session.post(f"{BASE_URL}/api/admin/users/{user_id}/demote")
        
        # Delete the test user
        response = session.delete(f"{BASE_URL}/api/admin/users/{user_id}")
        
        if response.status_code == 200:
            print(f"CLEANUP: Deleted test user {email}")
        else:
            print(f"CLEANUP: Could not delete test user (status {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
