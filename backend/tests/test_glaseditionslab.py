"""
GlasEditionsLab API Tests
Tests for: Auth, Books, Subscriptions, Exports (PDF, HTML, TXT, EPUB)
"""
import pytest
import requests
import os
import time
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test data
TEST_USER_EMAIL = f"test.user.{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = f"Test User {int(time.time())}"

# Global state for tests
test_state = {
    "access_token": None,
    "user_id": None,
    "book_id": None,
    "existing_book_id": "50ef06f8-0c24-4b89-ab77-9d74af14d72a"  # Pre-existing book with chapters
}


class TestHealthAndPlans:
    """Test basic API health and plans endpoints"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "GlasEditionsLab" in data["message"]
        print(f"✓ API root working: {data['message']}")
    
    def test_get_plans(self):
        """Test subscription plans endpoint"""
        response = requests.get(f"{BASE_URL}/api/plans")
        assert response.status_code == 200
        data = response.json()
        
        # Verify plans structure
        assert "plans" in data
        assert "single_book_price" in data
        assert data["single_book_price"] == 9.90
        
        # Verify 3 plans exist
        plans = data["plans"]
        assert len(plans) == 3
        
        # Verify plan details
        plan_ids = [p["id"] for p in plans]
        assert "debutant" in plan_ids
        assert "auteur" in plan_ids
        assert "ecrivain" in plan_ids
        
        # Verify Auteur is popular
        auteur_plan = next(p for p in plans if p["id"] == "auteur")
        assert auteur_plan["popular"] == True
        assert auteur_plan["price"] == 57.00
        
        # Verify Débutant plan
        debutant_plan = next(p for p in plans if p["id"] == "debutant")
        assert debutant_plan["price"] == 27.00
        assert debutant_plan["books_per_month"] == 3
        
        # Verify Écrivain plan
        ecrivain_plan = next(p for p in plans if p["id"] == "ecrivain")
        assert ecrivain_plan["price"] == 97.00
        assert ecrivain_plan["books_per_month"] == -1  # Unlimited
        
        print(f"✓ Plans API working: {len(plans)} plans returned")


class TestAuthentication:
    """Test user authentication flows"""
    
    def test_register_user(self):
        """Test user registration"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_USER_EMAIL
        assert data["user"]["name"] == TEST_USER_NAME
        assert data["user"]["subscription"] is None
        assert data["user"]["single_book_credits"] == 0
        
        # Store token for later tests
        test_state["access_token"] = data["access_token"]
        test_state["user_id"] = data["user"]["user_id"]
        
        print(f"✓ User registered: {TEST_USER_EMAIL}")
    
    def test_login_user(self):
        """Test user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["user"]["email"] == TEST_USER_EMAIL
        
        # Update token
        test_state["access_token"] = data["access_token"]
        print(f"✓ User logged in: {TEST_USER_EMAIL}")
    
    def test_get_current_user(self):
        """Test get current user endpoint"""
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == TEST_USER_EMAIL
        assert data["user_id"] == test_state["user_id"]
        print(f"✓ Current user retrieved: {data['email']}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")
    
    def test_duplicate_registration(self):
        """Test duplicate email registration"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": "AnotherPassword123!",
            "name": "Another User"
        })
        assert response.status_code == 400
        print("✓ Duplicate registration correctly rejected")


class TestBookCreationWithoutCredits:
    """Test book creation requires subscription/credits"""
    
    def test_create_book_without_credits_fails(self):
        """Test that book creation fails without subscription/credits"""
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        response = requests.post(f"{BASE_URL}/api/books", headers=headers, json={
            "title": "Test Book",
            "idea": "A test book idea",
            "genre": "fiction",
            "tone": "casual",
            "target_chapters": 10,
            "language": "français"
        })
        # Should fail with 403 - subscription required
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        print(f"✓ Book creation correctly requires subscription: {data['detail']}")


class TestStripeCheckout:
    """Test Stripe checkout session creation"""
    
    def test_create_subscription_checkout(self):
        """Test creating subscription checkout session"""
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        response = requests.post(f"{BASE_URL}/api/checkout/subscription", headers=headers, json={
            "plan_id": "auteur",
            "origin_url": "https://ai-book-gen-1.preview.emergentagent.com"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "checkout_url" in data
        assert "session_id" in data
        assert "stripe.com" in data["checkout_url"]
        print(f"✓ Subscription checkout created: {data['session_id'][:20]}...")
    
    def test_create_single_book_checkout(self):
        """Test creating single book checkout session"""
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        response = requests.post(f"{BASE_URL}/api/checkout/single-book", headers=headers, json={
            "origin_url": "https://ai-book-gen-1.preview.emergentagent.com"
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "checkout_url" in data
        assert "session_id" in data
        print(f"✓ Single book checkout created: {data['session_id'][:20]}...")
    
    def test_checkout_requires_auth(self):
        """Test checkout requires authentication"""
        response = requests.post(f"{BASE_URL}/api/checkout/subscription", json={
            "plan_id": "auteur",
            "origin_url": "https://ai-book-gen-1.preview.emergentagent.com"
        })
        assert response.status_code == 401
        print("✓ Checkout correctly requires authentication")


class TestExistingBook:
    """Test operations on existing book with chapters"""
    
    def test_get_existing_book(self):
        """Test getting existing book by ID"""
        book_id = test_state["existing_book_id"]
        response = requests.get(f"{BASE_URL}/api/books/{book_id}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == book_id
            print(f"✓ Existing book retrieved: {data['title']}")
            # Store for export tests
            test_state["book_id"] = book_id
        else:
            # Book might not exist, skip export tests
            print(f"⚠ Existing book not found (status {response.status_code}), will skip export tests")
            pytest.skip("Existing book not found")
    
    def test_update_book_title(self):
        """Test updating book title (PATCH)"""
        if not test_state.get("book_id"):
            pytest.skip("No book available for title update test")
        
        book_id = test_state["book_id"]
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        
        # First get current title
        response = requests.get(f"{BASE_URL}/api/books/{book_id}")
        original_title = response.json()["title"]
        
        # Update title
        new_title = f"Updated Title {int(time.time())}"
        response = requests.patch(f"{BASE_URL}/api/books/{book_id}", headers=headers, json={
            "title": new_title
        })
        
        # Note: May fail with 403 if user doesn't own the book
        if response.status_code == 200:
            data = response.json()
            assert data["title"] == new_title
            print(f"✓ Book title updated: {new_title}")
            
            # Restore original title
            requests.patch(f"{BASE_URL}/api/books/{book_id}", headers=headers, json={
                "title": original_title
            })
        elif response.status_code == 403:
            print("⚠ Cannot update book title - user doesn't own the book (expected)")
        else:
            print(f"⚠ Unexpected status: {response.status_code}")


class TestExportEndpoints:
    """Test all export endpoints (TXT, HTML, PDF, EPUB)"""
    
    def test_export_txt(self):
        """Test TXT export"""
        if not test_state.get("book_id"):
            pytest.skip("No book available for export test")
        
        book_id = test_state["book_id"]
        response = requests.get(f"{BASE_URL}/api/books/{book_id}/export/txt")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        assert len(response.content) > 0
        print(f"✓ TXT export working: {len(response.content)} bytes")
    
    def test_export_html(self):
        """Test HTML export"""
        if not test_state.get("book_id"):
            pytest.skip("No book available for export test")
        
        book_id = test_state["book_id"]
        response = requests.get(f"{BASE_URL}/api/books/{book_id}/export/html")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        content = response.content.decode('utf-8')
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        print(f"✓ HTML export working: {len(response.content)} bytes")
    
    def test_export_pdf(self):
        """Test PDF export"""
        if not test_state.get("book_id"):
            pytest.skip("No book available for export test")
        
        book_id = test_state["book_id"]
        response = requests.get(f"{BASE_URL}/api/books/{book_id}/export/pdf")
        
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("content-type", "")
        # PDF files start with %PDF
        assert response.content[:4] == b'%PDF'
        print(f"✓ PDF export working: {len(response.content)} bytes")
    
    def test_export_epub(self):
        """Test EPUB export (NEW FEATURE)"""
        if not test_state.get("book_id"):
            pytest.skip("No book available for export test")
        
        book_id = test_state["book_id"]
        response = requests.get(f"{BASE_URL}/api/books/{book_id}/export/epub")
        
        assert response.status_code == 200
        assert "application/epub+zip" in response.headers.get("content-type", "")
        # EPUB files are ZIP archives, start with PK
        assert response.content[:2] == b'PK'
        print(f"✓ EPUB export working: {len(response.content)} bytes")
    
    def test_export_invalid_format(self):
        """Test invalid export format"""
        if not test_state.get("book_id"):
            pytest.skip("No book available for export test")
        
        book_id = test_state["book_id"]
        response = requests.get(f"{BASE_URL}/api/books/{book_id}/export/invalid")
        
        assert response.status_code == 400
        print("✓ Invalid export format correctly rejected")


class TestBookOperationsWithCredits:
    """Test book operations after adding credits to user"""
    
    @pytest.fixture(autouse=True)
    def add_credits_to_user(self):
        """Add single book credits to test user via MongoDB"""
        import subprocess
        user_id = test_state.get("user_id")
        if not user_id:
            pytest.skip("No user ID available")
        
        # Add credits via mongosh
        cmd = f'''mongosh --quiet --eval "
            use('test_database');
            db.users.updateOne(
                {{'user_id': '{user_id}'}},
                {{'$set': {{'single_book_credits': 5}}}}
            );
            print('Credits added');
        "'''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Credits setup: {result.stdout.strip()}")
        yield
    
    def test_create_book_with_credits(self):
        """Test book creation with credits"""
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        response = requests.post(f"{BASE_URL}/api/books", headers=headers, json={
            "title": f"Test Book {int(time.time())}",
            "idea": "A fascinating story about AI and creativity",
            "genre": "fiction",
            "tone": "casual",
            "target_chapters": 10,
            "language": "français"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["status"] == "draft"
        assert data["target_chapters"] == 10
        
        test_state["created_book_id"] = data["id"]
        print(f"✓ Book created with credits: {data['id']}")
    
    def test_get_user_books(self):
        """Test getting user's books"""
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        response = requests.get(f"{BASE_URL}/api/books", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ User books retrieved: {len(data)} books")
    
    def test_generate_outline(self):
        """Test outline generation endpoint"""
        book_id = test_state.get("created_book_id")
        if not book_id:
            pytest.skip("No created book available")
        
        response = requests.post(f"{BASE_URL}/api/books/{book_id}/generate-outline")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "generating_outline"
        print(f"✓ Outline generation started for book: {book_id}")
    
    def test_delete_created_book(self):
        """Clean up - delete created test book"""
        book_id = test_state.get("created_book_id")
        if not book_id:
            pytest.skip("No created book to delete")
        
        response = requests.delete(f"{BASE_URL}/api/books/{book_id}")
        assert response.status_code == 200
        print(f"✓ Test book deleted: {book_id}")


class TestChapterOperations:
    """Test chapter generation and regeneration"""
    
    def test_generate_chapter_requires_outline(self):
        """Test that chapter generation requires outline first"""
        # Create a new book without outline
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        
        # First add credits
        import subprocess
        user_id = test_state.get("user_id")
        cmd = f'''mongosh --quiet --eval "
            use('test_database');
            db.users.updateOne(
                {{'user_id': '{user_id}'}},
                {{'$set': {{'single_book_credits': 5}}}}
            );
        "'''
        subprocess.run(cmd, shell=True, capture_output=True)
        
        # Create book
        response = requests.post(f"{BASE_URL}/api/books", headers=headers, json={
            "title": f"Chapter Test Book {int(time.time())}",
            "idea": "Test book for chapter operations",
            "genre": "fiction",
            "tone": "casual",
            "target_chapters": 10,
            "language": "français"
        })
        
        if response.status_code != 200:
            pytest.skip("Could not create book for chapter test")
        
        book_id = response.json()["id"]
        
        # Try to generate chapter without outline
        response = requests.post(f"{BASE_URL}/api/books/{book_id}/generate-chapter/1")
        assert response.status_code == 400
        assert "plan" in response.json()["detail"].lower()
        print("✓ Chapter generation correctly requires outline first")
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/books/{book_id}")
    
    def test_regenerate_chapter_endpoint(self):
        """Test chapter regeneration endpoint exists"""
        book_id = test_state.get("existing_book_id")
        if not book_id:
            pytest.skip("No existing book for regeneration test")
        
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        response = requests.post(f"{BASE_URL}/api/books/{book_id}/regenerate-chapter/1", headers=headers)
        
        # May return 200 (started) or 403 (not owner) or 400 (no outline)
        assert response.status_code in [200, 400, 403]
        print(f"✓ Regenerate chapter endpoint accessible (status: {response.status_code})")


class TestLogout:
    """Test logout functionality"""
    
    def test_logout(self):
        """Test user logout"""
        headers = {"Authorization": f"Bearer {test_state['access_token']}"}
        response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        assert response.status_code == 200
        print("✓ User logged out successfully")


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup test data after all tests"""
    yield
    # Cleanup test user and books
    import subprocess
    cmd = f'''mongosh --quiet --eval "
        use('test_database');
        db.users.deleteMany({{'email': /test\\.user\\./}});
        db.books.deleteMany({{'title': /Test Book/}});
        db.books.deleteMany({{'title': /Chapter Test Book/}});
        print('Cleanup completed');
    "'''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"\nCleanup: {result.stdout.strip()}")
