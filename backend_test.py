#!/usr/bin/env python3
"""
GlasEditionsLab Backend API Testing Suite
Tests all API endpoints including authentication, book generation, and cover generation
"""

import requests
import sys
import json
import time
from datetime import datetime

class GlasEditionsLabAPITester:
    def __init__(self, base_url="https://ai-booksmith-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_book_id = None
        self.auth_token = None
        self.test_user_email = "test@example.com"
        self.test_user_password = "test123"
        self.session = requests.Session()

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else None
            
            self.log_test(
                "API Root Endpoint",
                success,
                f"Status: {response.status_code}",
                data
            )
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Error: {str(e)}")
            return False

    def test_register_user(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        register_data = {
            "name": f"Test User {timestamp}",
            "email": f"test.user.{timestamp}@example.com",
            "password": "testpass123"
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/auth/register",
                json=register_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and data:
                self.auth_token = data.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                details = f"User registered: {register_data['email']}"
            else:
                details = f"Status: {response.status_code}"
                if not success:
                    try:
                        error_data = response.json()
                        details += f" - {error_data.get('detail', 'Unknown error')}"
                    except:
                        pass
            
            self.log_test("Register User", success, details, data)
            return success
        except Exception as e:
            self.log_test("Register User", False, f"Error: {str(e)}")
            return False

    def test_login_user(self):
        """Test user login with existing credentials"""
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and data:
                self.auth_token = data.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                details = f"Login successful for: {login_data['email']}"
            else:
                details = f"Status: {response.status_code}"
                if not success:
                    try:
                        error_data = response.json()
                        details += f" - {error_data.get('detail', 'Unknown error')}"
                    except:
                        pass
            
            self.log_test("Login User", success, details, data)
            return success
        except Exception as e:
            self.log_test("Login User", False, f"Error: {str(e)}")
            return False

    def test_get_current_user(self):
        """Test getting current authenticated user"""
        try:
            response = self.session.get(f"{self.api_url}/auth/me", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and data:
                details = f"User info retrieved: {data.get('email', 'Unknown')}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Current User", success, details, data)
            return success
        except Exception as e:
            self.log_test("Get Current User", False, f"Error: {str(e)}")
            return False

    def test_create_book(self):
        """Test book creation"""
        book_data = {
            "title": f"Test Book {datetime.now().strftime('%H%M%S')}",
            "idea": "Un livre de test sur l'intelligence artificielle et ses applications dans la littérature moderne.",
            "genre": "fiction",
            "tone": "literary",
            "target_chapters": 15,
            "language": "français",
            "additional_info": "Style narratif avec des éléments de science-fiction"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/books",
                json=book_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and data:
                self.created_book_id = data.get('id')
                details = f"Book created with ID: {self.created_book_id}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Create Book", success, details, data)
            return success
        except Exception as e:
            self.log_test("Create Book", False, f"Error: {str(e)}")
            return False

    def test_get_books(self):
        """Test getting all books"""
        try:
            response = requests.get(f"{self.api_url}/books", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and isinstance(data, list):
                details = f"Retrieved {len(data)} books"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get All Books", success, details, data)
            return success
        except Exception as e:
            self.log_test("Get All Books", False, f"Error: {str(e)}")
            return False

    def test_get_book_by_id(self):
        """Test getting specific book by ID"""
        if not self.created_book_id:
            self.log_test("Get Book by ID", False, "No book ID available (create book first)")
            return False
        
        try:
            response = requests.get(f"{self.api_url}/books/{self.created_book_id}", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and data:
                details = f"Retrieved book: {data.get('title', 'Unknown')}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Book by ID", success, details, data)
            return success
        except Exception as e:
            self.log_test("Get Book by ID", False, f"Error: {str(e)}")
            return False

    def test_generate_outline(self):
        """Test outline generation"""
        if not self.created_book_id:
            self.log_test("Generate Outline", False, "No book ID available")
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/books/{self.created_book_id}/generate-outline",
                timeout=30
            )
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                details = "Outline generation started"
                # Wait a bit and check status
                time.sleep(3)
                status_response = requests.get(f"{self.api_url}/books/{self.created_book_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    details += f" - Status: {status_data.get('status', 'unknown')}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Generate Outline", success, details, data)
            return success
        except Exception as e:
            self.log_test("Generate Outline", False, f"Error: {str(e)}")
            return False

    def test_generate_all_chapters(self):
        """Test generating all chapters (will start the process)"""
        if not self.created_book_id:
            self.log_test("Generate All Chapters", False, "No book ID available")
            return False
        
        try:
            # First check if outline exists
            book_response = requests.get(f"{self.api_url}/books/{self.created_book_id}")
            if book_response.status_code != 200:
                self.log_test("Generate All Chapters", False, "Cannot retrieve book")
                return False
            
            book_data = book_response.json()
            if not book_data.get('outline'):
                self.log_test("Generate All Chapters", False, "No outline available (generate outline first)")
                return False
            
            response = requests.post(
                f"{self.api_url}/books/{self.created_book_id}/generate-all",
                timeout=30
            )
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if success:
                details = "Chapter generation started"
            
            self.log_test("Generate All Chapters", success, details, data)
            return success
        except Exception as e:
            self.log_test("Generate All Chapters", False, f"Error: {str(e)}")
            return False

    def test_export_txt(self):
        """Test TXT export"""
        if not self.created_book_id:
            self.log_test("Export TXT", False, "No book ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.api_url}/books/{self.created_book_id}/export/txt",
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                content_length = len(response.content)
                details = f"TXT export successful - {content_length} bytes"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Export TXT", success, details)
            return success
        except Exception as e:
            self.log_test("Export TXT", False, f"Error: {str(e)}")
            return False

    def test_export_html(self):
        """Test HTML export"""
        if not self.created_book_id:
            self.log_test("Export HTML", False, "No book ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.api_url}/books/{self.created_book_id}/export/html",
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                content_length = len(response.content)
                details = f"HTML export successful - {content_length} bytes"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Export HTML", success, details)
            return success
        except Exception as e:
            self.log_test("Export HTML", False, f"Error: {str(e)}")
            return False

    def test_delete_book(self):
        """Test book deletion"""
        if not self.created_book_id:
            self.log_test("Delete Book", False, "No book ID available")
            return False
        
        try:
            response = requests.delete(f"{self.api_url}/books/{self.created_book_id}", timeout=10)
            success = response.status_code == 200
            
            details = f"Status: {response.status_code}"
            if success:
                details = "Book deleted successfully"
            
            self.log_test("Delete Book", success, details)
            return success
        except Exception as e:
            self.log_test("Delete Book", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting OneBookLab API Tests")
        print(f"📡 Testing API at: {self.api_url}")
        print("=" * 50)
        
        # Core API tests
        self.test_api_root()
        self.test_create_book()
        self.test_get_books()
        self.test_get_book_by_id()
        
        # AI Generation tests (these may take time)
        print("\n🤖 Testing AI Generation Features...")
        self.test_generate_outline()
        
        # Wait for outline to be ready before testing chapter generation
        if self.created_book_id:
            print("⏳ Waiting for outline generation to complete...")
            for i in range(10):  # Wait up to 30 seconds
                time.sleep(3)
                try:
                    response = requests.get(f"{self.api_url}/books/{self.created_book_id}")
                    if response.status_code == 200:
                        book_data = response.json()
                        status = book_data.get('status')
                        print(f"    Status check {i+1}: {status}")
                        if status == 'outline_ready':
                            break
                        elif status == 'error':
                            print(f"    Error: {book_data.get('error_message', 'Unknown error')}")
                            break
                except:
                    pass
        
        self.test_generate_all_chapters()
        
        # Export tests
        print("\n📄 Testing Export Features...")
        self.test_export_txt()
        self.test_export_html()
        
        # Cleanup
        print("\n🧹 Cleanup...")
        self.test_delete_book()
        
        # Results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed. Check details above.")
            return 1

def main():
    tester = OneBookLabAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())