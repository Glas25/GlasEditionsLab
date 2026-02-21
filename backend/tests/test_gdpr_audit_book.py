"""
Test GDPR Export, Audit Log, and Book Creation Bug Fix
Tests for iteration 10 features:
1. GDPR data export endpoint
2. Admin audit log functionality
3. Book creation with auth token
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "glaseditionslab@gmail.com"
ADMIN_PASSWORD = "Admin123!"


class TestGDPRDataExport:
    """Tests for GET /api/account/export-data (GDPR compliance)"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_export_data_requires_auth(self):
        """Test that export-data endpoint returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/account/export-data")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/account/export-data returns 401 without auth")
    
    def test_export_data_returns_json_with_auth(self, admin_token):
        """Test that export-data returns valid JSON with auth token"""
        response = requests.get(
            f"{BASE_URL}/api/account/export-data",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check Content-Type
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected application/json, got {content_type}"
        print("PASS: GET /api/account/export-data returns 200 with JSON content")
    
    def test_export_data_has_content_disposition_header(self, admin_token):
        """Test that export-data has Content-Disposition header for download"""
        response = requests.get(
            f"{BASE_URL}/api/account/export-data",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition, f"Expected attachment header, got: {content_disposition}"
        assert "filename=" in content_disposition, f"Expected filename in header, got: {content_disposition}"
        print(f"PASS: Content-Disposition header present: {content_disposition}")
    
    def test_export_data_structure(self, admin_token):
        """Test that export-data JSON has required fields"""
        response = requests.get(
            f"{BASE_URL}/api/account/export-data",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required top-level fields
        assert "personal_information" in data, "Missing 'personal_information' field"
        assert "subscription" in data, "Missing 'subscription' field"
        assert "books" in data, "Missing 'books' field"
        assert "total_books" in data, "Missing 'total_books' field"
        assert "export_date" in data, "Missing 'export_date' field"
        
        # Check personal_information structure
        personal_info = data["personal_information"]
        assert "user_id" in personal_info, "Missing user_id in personal_information"
        assert "name" in personal_info, "Missing name in personal_information"
        assert "email" in personal_info, "Missing email in personal_information"
        
        # Check subscription structure
        sub = data["subscription"]
        assert "plan" in sub, "Missing plan in subscription"
        
        # Verify books is a list
        assert isinstance(data["books"], list), "books should be a list"
        assert isinstance(data["total_books"], int), "total_books should be an integer"
        
        print(f"PASS: Export data structure is valid with {data['total_books']} books")


class TestAuditLog:
    """Tests for GET /api/admin/audit-log and audit logging functionality"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return response.json().get("access_token")
    
    @pytest.fixture
    def test_user(self, admin_token):
        """Create a test user for promotion/demotion/deletion testing"""
        unique_id = uuid.uuid4().hex[:8]
        email = f"TEST_audit_{unique_id}@test.com"
        password = "TestPass123!"
        name = f"Test Audit User {unique_id}"
        
        # Register test user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": password,
            "name": name
        })
        
        if response.status_code != 200:
            pytest.skip(f"Failed to create test user: {response.status_code} - {response.text}")
        
        user_data = response.json()
        return {
            "user_id": user_data["user"]["user_id"],
            "email": email,
            "name": name
        }
    
    def test_audit_log_requires_admin(self):
        """Test that audit-log endpoint returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/audit-log")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/admin/audit-log returns 401 without auth")
    
    def test_audit_log_returns_paginated_logs(self, admin_token):
        """Test that audit-log returns paginated structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"page": 1, "limit": 10}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "logs" in data, "Missing 'logs' field"
        assert "total" in data, "Missing 'total' field"
        assert "page" in data, "Missing 'page' field"
        assert "total_pages" in data, "Missing 'total_pages' field"
        assert isinstance(data["logs"], list), "logs should be a list"
        
        print(f"PASS: Audit log returns paginated structure with {data['total']} total entries")
    
    def test_promotion_creates_audit_entry(self, admin_token, test_user):
        """Test that promoting a user creates an audit log entry"""
        # Get initial audit log count
        initial_response = requests.get(
            f"{BASE_URL}/api/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        initial_total = initial_response.json().get("total", 0)
        
        # Promote the test user
        promote_response = requests.post(
            f"{BASE_URL}/api/admin/users/{test_user['user_id']}/promote",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert promote_response.status_code == 200, f"Promotion failed: {promote_response.status_code} - {promote_response.text}"
        
        # Check audit log for new entry
        audit_response = requests.get(
            f"{BASE_URL}/api/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"page": 1, "limit": 10}
        )
        assert audit_response.status_code == 200
        
        data = audit_response.json()
        new_total = data.get("total", 0)
        
        # Verify count increased
        assert new_total > initial_total, f"Audit log count should increase after promotion"
        
        # Verify the latest entry is for promotion
        logs = data.get("logs", [])
        assert len(logs) > 0, "No audit logs found after promotion"
        
        latest_log = logs[0]
        assert latest_log.get("action") == "promotion", f"Expected 'promotion' action, got: {latest_log.get('action')}"
        assert latest_log.get("target_email") == test_user["email"], f"Target email mismatch"
        
        print(f"PASS: Promotion creates audit entry with action='promotion' for {test_user['email']}")
    
    def test_demotion_creates_audit_entry(self, admin_token, test_user):
        """Test that demoting a user creates an audit log entry"""
        # First, promote the user
        requests.post(
            f"{BASE_URL}/api/admin/users/{test_user['user_id']}/promote",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Get current audit log count
        initial_response = requests.get(
            f"{BASE_URL}/api/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        initial_total = initial_response.json().get("total", 0)
        
        # Demote the test user
        demote_response = requests.post(
            f"{BASE_URL}/api/admin/users/{test_user['user_id']}/demote",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert demote_response.status_code == 200, f"Demotion failed: {demote_response.status_code} - {demote_response.text}"
        
        # Check audit log for new entry
        audit_response = requests.get(
            f"{BASE_URL}/api/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"page": 1, "limit": 10}
        )
        
        data = audit_response.json()
        new_total = data.get("total", 0)
        
        assert new_total > initial_total, "Audit log count should increase after demotion"
        
        logs = data.get("logs", [])
        latest_log = logs[0]
        assert latest_log.get("action") == "révocation", f"Expected 'révocation' action, got: {latest_log.get('action')}"
        assert latest_log.get("target_email") == test_user["email"]
        
        print(f"PASS: Demotion creates audit entry with action='révocation' for {test_user['email']}")
    
    def test_deletion_creates_audit_entry(self, admin_token, test_user):
        """Test that deleting a user creates an audit log entry"""
        # Get current audit log count
        initial_response = requests.get(
            f"{BASE_URL}/api/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        initial_total = initial_response.json().get("total", 0)
        
        # Delete the test user
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/users/{test_user['user_id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200, f"Deletion failed: {delete_response.status_code} - {delete_response.text}"
        
        # Check audit log for new entry
        audit_response = requests.get(
            f"{BASE_URL}/api/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"page": 1, "limit": 10}
        )
        
        data = audit_response.json()
        new_total = data.get("total", 0)
        
        assert new_total > initial_total, "Audit log count should increase after deletion"
        
        logs = data.get("logs", [])
        latest_log = logs[0]
        assert latest_log.get("action") == "suppression", f"Expected 'suppression' action, got: {latest_log.get('action')}"
        assert latest_log.get("target_email") == test_user["email"]
        
        print(f"PASS: Deletion creates audit entry with action='suppression' for {test_user['email']}")


class TestBookCreationBugFix:
    """Tests for POST /api/books with auth token (bug fix verification)"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_book_creation_requires_auth(self):
        """Test that book creation returns 401 without auth"""
        book_data = {
            "title": "Test Book Without Auth",
            "idea": "A test book to verify auth is required",
            "genre": "fiction",
            "tone": "literary",
            "target_chapters": 10,
            "language": "français"
        }
        response = requests.post(f"{BASE_URL}/api/books", json=book_data)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: POST /api/books returns 401 without auth")
    
    def test_book_creation_works_with_auth_token(self, admin_token):
        """Test that book creation works with valid auth token"""
        unique_id = uuid.uuid4().hex[:8]
        book_data = {
            "title": f"TEST_Book_{unique_id}",
            "idea": "A test book to verify the bug fix - book creation with auth token",
            "genre": "fiction",
            "tone": "literary",
            "target_chapters": 10,
            "language": "français",
            "additional_info": "Created for testing purposes"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/books",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain book id"
        assert data["title"] == book_data["title"], "Title should match"
        assert data["genre"] == book_data["genre"], "Genre should match"
        assert data["tone"] == book_data["tone"], "Tone should match"
        assert data["target_chapters"] == book_data["target_chapters"], "Chapter count should match"
        assert data["status"] == "draft", f"Status should be 'draft', got: {data['status']}"
        
        book_id = data["id"]
        print(f"PASS: Book created successfully with id: {book_id}")
        
        # Cleanup: delete the test book
        cleanup_response = requests.delete(f"{BASE_URL}/api/books/{book_id}")
        if cleanup_response.status_code == 200:
            print(f"Cleanup: Test book {book_id} deleted")
        
        return data
    
    def test_book_creation_returns_user_id(self, admin_token):
        """Test that created book has user_id associated"""
        unique_id = uuid.uuid4().hex[:8]
        book_data = {
            "title": f"TEST_UserIdBook_{unique_id}",
            "idea": "Test book to verify user_id is set",
            "genre": "thriller",
            "tone": "dramatic",
            "target_chapters": 10,
            "language": "français"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/books",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("user_id") is not None, "Created book should have user_id set"
        assert data["user_id"].startswith("user_"), f"user_id should be valid format, got: {data['user_id']}"
        
        print(f"PASS: Book created with user_id: {data['user_id']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/books/{data['id']}")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json().get("access_token")
    
    def test_cleanup_test_users(self, admin_token):
        """Cleanup any remaining test users from this test run"""
        # Get all users
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"search": "TEST_audit_", "limit": 100}
        )
        
        if response.status_code != 200:
            print(f"Could not fetch users for cleanup: {response.status_code}")
            return
        
        users = response.json().get("users", [])
        deleted_count = 0
        
        for user in users:
            if user.get("email", "").startswith("TEST_audit_"):
                del_response = requests.delete(
                    f"{BASE_URL}/api/admin/users/{user['user_id']}",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                if del_response.status_code == 200:
                    deleted_count += 1
        
        print(f"Cleanup: Deleted {deleted_count} test users")
        # This is cleanup, don't fail if nothing to delete
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
