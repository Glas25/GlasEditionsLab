"""
Admin Dashboard API Tests
Tests for: GET /api/admin/stats, GET /api/admin/users, GET /api/admin/users/export, DELETE /api/admin/users/{user_id}
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

# Using public URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "glaseditionslab@gmail.com"
ADMIN_PASSWORD = "Admin123!"

# Store for cleanup
test_created_users = []


class TestAdminAuth:
    """Test admin authentication requirements"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_admin_token(self):
        """Login as admin and get token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def test_admin_stats_requires_auth(self):
        """GET /api/admin/stats - returns 401 without token"""
        response = self.session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/admin/stats requires authentication (401)")
    
    def test_admin_users_requires_auth(self):
        """GET /api/admin/users - returns 401 without token"""
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/admin/users requires authentication (401)")
    
    def test_admin_export_requires_auth(self):
        """GET /api/admin/users/export - returns 401 without token"""
        response = self.session.get(f"{BASE_URL}/api/admin/users/export")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/admin/users/export requires authentication (401)")
    
    def test_admin_delete_requires_auth(self):
        """DELETE /api/admin/users/{user_id} - returns 401 without token"""
        response = self.session.delete(f"{BASE_URL}/api/admin/users/fake_user_id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: DELETE /api/admin/users requires authentication (401)")


class TestAdminForbiddenForNonAdmin:
    """Test that non-admin users get 403 on admin endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Create a test user
        self.test_email = f"TEST_admin_nonadmin_{uuid.uuid4().hex[:8]}@test.com"
        self.test_password = "Test123!"
        
        response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Test Non-Admin User"
        })
        if response.status_code == 200:
            self.non_admin_token = response.json().get("access_token")
            self.test_user_id = response.json().get("user", {}).get("user_id")
            test_created_users.append(self.test_user_id)
        else:
            pytest.skip(f"Failed to create test user: {response.status_code}")
    
    def test_non_admin_stats_forbidden(self):
        """GET /api/admin/stats - returns 403 for non-admin"""
        response = self.session.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {self.non_admin_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: /api/admin/stats returns 403 for non-admin")
    
    def test_non_admin_users_forbidden(self):
        """GET /api/admin/users - returns 403 for non-admin"""
        response = self.session.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {self.non_admin_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: /api/admin/users returns 403 for non-admin")
    
    def test_non_admin_export_forbidden(self):
        """GET /api/admin/users/export - returns 403 for non-admin"""
        response = self.session.get(
            f"{BASE_URL}/api/admin/users/export",
            headers={"Authorization": f"Bearer {self.non_admin_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: /api/admin/users/export returns 403 for non-admin")
    
    def test_non_admin_delete_forbidden(self):
        """DELETE /api/admin/users/{user_id} - returns 403 for non-admin"""
        response = self.session.delete(
            f"{BASE_URL}/api/admin/users/some_user_id",
            headers={"Authorization": f"Bearer {self.non_admin_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: DELETE /api/admin/users returns 403 for non-admin")


class TestAdminStats:
    """Test admin stats endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        self.admin_token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_admin_stats_returns_correct_fields(self):
        """GET /api/admin/stats - returns all required fields"""
        response = self.session.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        required_fields = ["total_users", "total_books", "books_this_month", "subscription_distribution", "no_plan_users", "estimated_monthly_revenue"]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Validate data types
        assert isinstance(data["total_users"], int), "total_users should be int"
        assert isinstance(data["total_books"], int), "total_books should be int"
        assert isinstance(data["books_this_month"], int), "books_this_month should be int"
        assert isinstance(data["subscription_distribution"], dict), "subscription_distribution should be dict"
        assert isinstance(data["no_plan_users"], int), "no_plan_users should be int"
        assert isinstance(data["estimated_monthly_revenue"], (int, float)), "estimated_monthly_revenue should be numeric"
        
        print(f"PASS: /api/admin/stats returns correct fields: {list(data.keys())}")
        print(f"  - total_users: {data['total_users']}")
        print(f"  - total_books: {data['total_books']}")
        print(f"  - subscription_distribution: {data['subscription_distribution']}")


class TestAdminUsers:
    """Test admin users list endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        self.admin_token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_admin_users_returns_paginated_list(self):
        """GET /api/admin/users - returns paginated user list"""
        response = self.session.get(f"{BASE_URL}/api/admin/users", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "users" in data, "Response should contain 'users'"
        assert "total" in data, "Response should contain 'total'"
        assert "page" in data, "Response should contain 'page'"
        assert "total_pages" in data, "Response should contain 'total_pages'"
        
        # Check user fields
        if len(data["users"]) > 0:
            user = data["users"][0]
            required_user_fields = ["user_id", "name", "email", "subscription", "books_count", "created_at", "is_admin"]
            for field in required_user_fields:
                assert field in user, f"User missing field: {field}"
        
        print(f"PASS: /api/admin/users returns paginated list with {len(data['users'])} users (total: {data['total']})")
    
    def test_admin_users_search_filter(self):
        """GET /api/admin/users?search=test - filters by search term"""
        response = self.session.get(f"{BASE_URL}/api/admin/users?search=test", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # All returned users should have 'test' in name or email (case insensitive)
        for user in data["users"]:
            name_match = "test" in user.get("name", "").lower()
            email_match = "test" in user.get("email", "").lower()
            assert name_match or email_match, f"User {user['email']} does not match search 'test'"
        
        print(f"PASS: /api/admin/users?search=test filters correctly ({len(data['users'])} results)")
    
    def test_admin_users_plan_filter_sans_abonnement(self):
        """GET /api/admin/users?plan=sans_abonnement - filters users without subscription"""
        response = self.session.get(f"{BASE_URL}/api/admin/users?plan=sans_abonnement", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        for user in data["users"]:
            # Users without subscription should not be admin and have no subscription
            assert not user.get("is_admin"), f"Admin user {user['email']} should not appear in sans_abonnement filter"
            assert user.get("subscription") is None or user.get("subscription") == "", f"User {user['email']} has subscription"
        
        print(f"PASS: /api/admin/users?plan=sans_abonnement filters correctly ({len(data['users'])} results)")
    
    def test_admin_users_pagination(self):
        """GET /api/admin/users - pagination works correctly"""
        response = self.session.get(f"{BASE_URL}/api/admin/users?page=1&limit=5", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1, "Page should be 1"
        assert len(data["users"]) <= 5, "Should return at most 5 users"
        
        print(f"PASS: /api/admin/users pagination works (page {data['page']}/{data['total_pages']})")


class TestAdminUsersExport:
    """Test admin users CSV export"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        self.admin_token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_export_returns_csv(self):
        """GET /api/admin/users/export - returns CSV file"""
        # Using token as query param (as per frontend implementation)
        response = self.session.get(f"{BASE_URL}/api/admin/users/export?token={self.admin_token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected text/csv, got {content_type}"
        
        # Check content disposition for filename
        content_disp = response.headers.get("Content-Disposition", "")
        assert "filename=" in content_disp, "Should have filename in Content-Disposition"
        assert "utilisateurs_" in content_disp, "Filename should start with 'utilisateurs_'"
        
        # Check CSV headers (first line)
        csv_content = response.content.decode('utf-8-sig')
        first_line = csv_content.split('\n')[0]
        expected_headers = ["Nom", "Email", "Abonnement", "Crédits livres", "Livres créés", "Livres ce mois", "Date d'inscription"]
        for header in expected_headers:
            assert header in first_line, f"CSV missing header: {header}"
        
        print(f"PASS: /api/admin/users/export returns valid CSV with correct headers")
    
    def test_export_with_search_filter(self):
        """GET /api/admin/users/export?search=glas - applies search filter"""
        response = self.session.get(f"{BASE_URL}/api/admin/users/export?search=glas&token={self.admin_token}")
        assert response.status_code == 200
        
        csv_content = response.content.decode('utf-8-sig')
        lines = [l for l in csv_content.split('\n') if l.strip()]
        
        # Check that rows contain 'glas'
        for line in lines[1:]:  # Skip header
            assert "glas" in line.lower(), f"Row should contain 'glas': {line}"
        
        print(f"PASS: /api/admin/users/export applies search filter correctly")


class TestAdminDeleteUser:
    """Test admin delete user endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        self.admin_token = response.json().get("access_token")
        self.admin_user_id = response.json().get("user", {}).get("user_id")
        self.headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_delete_non_admin_user(self):
        """DELETE /api/admin/users/{user_id} - deletes non-admin user and books"""
        # First create a test user
        test_email = f"TEST_admin_delete_{uuid.uuid4().hex[:8]}@test.com"
        reg_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "Test123!",
            "name": "Test User To Delete"
        })
        assert reg_response.status_code == 200, f"Failed to create test user: {reg_response.status_code}"
        test_user_id = reg_response.json().get("user", {}).get("user_id")
        
        # Delete the user
        delete_response = self.session.delete(
            f"{BASE_URL}/api/admin/users/{test_user_id}",
            headers=self.headers
        )
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        
        data = delete_response.json()
        assert "message" in data, "Response should contain 'message'"
        assert test_email in data["message"], f"Message should mention deleted email: {data['message']}"
        
        # Verify user is deleted by trying to login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "Test123!"
        })
        assert login_response.status_code == 401, "Deleted user should not be able to login"
        
        print(f"PASS: DELETE /api/admin/users/{test_user_id} deleted user successfully")
    
    def test_cannot_delete_admin_user(self):
        """DELETE /api/admin/users/{admin_user_id} - returns 400 for admin deletion"""
        delete_response = self.session.delete(
            f"{BASE_URL}/api/admin/users/{self.admin_user_id}",
            headers=self.headers
        )
        assert delete_response.status_code == 400, f"Expected 400, got {delete_response.status_code}"
        
        data = delete_response.json()
        assert "administrateur" in data.get("detail", "").lower(), f"Should mention admin: {data}"
        
        print(f"PASS: DELETE /api/admin/users cannot delete admin (400)")
    
    def test_delete_nonexistent_user(self):
        """DELETE /api/admin/users/{fake_id} - returns 404"""
        delete_response = self.session.delete(
            f"{BASE_URL}/api/admin/users/nonexistent_user_id_12345",
            headers=self.headers
        )
        assert delete_response.status_code == 404, f"Expected 404, got {delete_response.status_code}"
        
        print(f"PASS: DELETE /api/admin/users returns 404 for nonexistent user")


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_users():
    """Cleanup test users created during tests"""
    yield
    
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    # Login as admin
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all users and delete TEST_ prefixed ones
        users_response = session.get(f"{BASE_URL}/api/admin/users?limit=100", headers=headers)
        if users_response.status_code == 200:
            users = users_response.json().get("users", [])
            for user in users:
                if user.get("email", "").startswith("TEST_"):
                    session.delete(f"{BASE_URL}/api/admin/users/{user['user_id']}", headers=headers)
                    print(f"Cleaned up test user: {user['email']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
