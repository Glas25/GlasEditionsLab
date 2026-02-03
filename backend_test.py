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
            response = self.session.post(
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
                if not success:
                    try:
                        error_data = response.json()
                        details += f" - {error_data.get('detail', 'Unknown error')}"
                    except:
                        pass
            
            self.log_test("Create Book", success, details, data)
            return success
        except Exception as e:
            self.log_test("Create Book", False, f"Error: {str(e)}")
            return False

    def test_get_books(self):
        """Test getting all books"""
        try:
            response = self.session.get(f"{self.api_url}/books", timeout=10)
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
            response = self.session.get(f"{self.api_url}/books/{self.created_book_id}", timeout=10)
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
            response = self.session.post(
                f"{self.api_url}/books/{self.created_book_id}/generate-outline",
                timeout=30
            )
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                details = "Outline generation started"
                # Wait a bit and check status
                time.sleep(3)
                status_response = self.session.get(f"{self.api_url}/books/{self.created_book_id}")
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

    def test_generate_cover(self):
        """Test cover generation"""
        if not self.created_book_id:
            self.log_test("Generate Cover", False, "No book ID available")
            return False
        
        try:
            cover_data = {
                "prompt": "A beautiful book cover with elegant typography and artistic elements"
            }
            
            response = self.session.post(
                f"{self.api_url}/books/{self.created_book_id}/generate-cover",
                json=cover_data,
                headers={"Content-Type": "application/json"},
                timeout=60  # Cover generation may take longer
            )
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                details = "Cover generation started"
                # Wait a bit and check status
                time.sleep(5)
                status_response = self.session.get(f"{self.api_url}/books/{self.created_book_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    details += f" - Status: {status_data.get('status', 'unknown')}"
                    if status_data.get('cover_image'):
                        details += " - Cover image generated"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Generate Cover", success, details, data)
            return success
        except Exception as e:
            self.log_test("Generate Cover", False, f"Error: {str(e)}")
            return False

    def test_generate_all_chapters(self):
        """Test generating all chapters (will start the process)"""
        if not self.created_book_id:
            self.log_test("Generate All Chapters", False, "No book ID available")
            return False
        
        try:
            # First check if outline exists
            book_response = self.session.get(f"{self.api_url}/books/{self.created_book_id}")
            if book_response.status_code != 200:
                self.log_test("Generate All Chapters", False, "Cannot retrieve book")
                return False
            
            book_data = book_response.json()
            if not book_data.get('outline'):
                self.log_test("Generate All Chapters", False, "No outline available (generate outline first)")
                return False
            
            response = self.session.post(
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
            response = self.session.get(
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
            response = self.session.get(
                f"{self.api_url}/books/{self.created_book_id}/export/html",
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                content_length = len(response.content)
                details = f"HTML export successful - {content_length} bytes"
                # Check if HTML contains cover image and table of contents
                content = response.text
                has_cover = 'cover' in content.lower()
                has_toc = 'table des matières' in content.lower() or 'toc' in content.lower()
                details += f" - Cover: {has_cover}, TOC: {has_toc}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Export HTML", success, details)
            return success
        except Exception as e:
            self.log_test("Export HTML", False, f"Error: {str(e)}")
            return False

    def test_export_pdf(self):
        """Test PDF export"""
        if not self.created_book_id:
            self.log_test("Export PDF", False, "No book ID available")
            return False
        
        try:
            response = self.session.get(
                f"{self.api_url}/books/{self.created_book_id}/export/pdf",
                timeout=30  # PDF generation may take longer
            )
            success = response.status_code == 200
            
            if success:
                content_length = len(response.content)
                details = f"PDF export successful - {content_length} bytes"
                # Check if it's actually a PDF
                is_pdf = response.content.startswith(b'%PDF')
                details += f" - Valid PDF: {is_pdf}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Export PDF", success, details)
            return success
        except Exception as e:
            self.log_test("Export PDF", False, f"Error: {str(e)}")
            return False

    def test_get_plans(self):
        """Test getting subscription plans"""
        try:
            response = self.session.get(f"{self.api_url}/plans", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and data:
                plans = data.get('plans', [])
                single_book_price = data.get('single_book_price')
                details = f"Retrieved {len(plans)} plans, single book price: {single_book_price}€"
                
                # Check specific requirements from review request
                auteur_plan = next((p for p in plans if p['id'] == 'auteur'), None)
                if auteur_plan and auteur_plan.get('popular'):
                    details += " - Auteur plan marked as popular ✓"
                else:
                    details += " - Auteur plan NOT marked as popular ✗"
                
                if single_book_price == 9.90:
                    details += " - Single book price correct ✓"
                else:
                    details += f" - Single book price incorrect (expected 9.90€) ✗"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Get Subscription Plans", success, details, data)
            return success
        except Exception as e:
            self.log_test("Get Subscription Plans", False, f"Error: {str(e)}")
            return False

    def test_book_title_update(self):
        """Test book title update functionality"""
        if not self.created_book_id:
            self.log_test("Update Book Title", False, "No book ID available")
            return False
        
        try:
            new_title = f"Updated Test Book {datetime.now().strftime('%H%M%S')}"
            update_data = {"title": new_title}
            
            response = self.session.patch(
                f"{self.api_url}/books/{self.created_book_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success and data:
                updated_title = data.get('title')
                if updated_title == new_title:
                    details = f"Title updated successfully to: {updated_title}"
                else:
                    details = f"Title update failed - expected: {new_title}, got: {updated_title}"
                    success = False
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Update Book Title", success, details, data)
            return success
        except Exception as e:
            self.log_test("Update Book Title", False, f"Error: {str(e)}")
            return False

    def test_regenerate_chapter(self):
        """Test chapter regeneration functionality"""
        if not self.created_book_id:
            self.log_test("Regenerate Chapter", False, "No book ID available")
            return False
        
        try:
            # First check if book has outline with completed chapters
            book_response = self.session.get(f"{self.api_url}/books/{self.created_book_id}")
            if book_response.status_code != 200:
                self.log_test("Regenerate Chapter", False, "Cannot retrieve book")
                return False
            
            book_data = book_response.json()
            outline = book_data.get('outline', [])
            
            # Find a completed chapter to regenerate
            completed_chapter = None
            for chapter in outline:
                if chapter.get('status') == 'completed':
                    completed_chapter = chapter
                    break
            
            if not completed_chapter:
                self.log_test("Regenerate Chapter", False, "No completed chapters available for regeneration")
                return False
            
            chapter_num = completed_chapter['number']
            response = self.session.post(
                f"{self.api_url}/books/{self.created_book_id}/regenerate-chapter/{chapter_num}",
                timeout=30
            )
            
            success = response.status_code == 200
            data = response.json() if success else None
            
            if success:
                details = f"Chapter {chapter_num} regeneration started"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Regenerate Chapter", success, details, data)
            return success
        except Exception as e:
            self.log_test("Regenerate Chapter", False, f"Error: {str(e)}")
            return False
        """Test user logout"""
        try:
            response = self.session.post(f"{self.api_url}/auth/logout", timeout=10)
            success = response.status_code == 200
            
            if success:
                # Clear auth token
                self.auth_token = None
                if 'Authorization' in self.session.headers:
                    del self.session.headers['Authorization']
                details = "Logout successful"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Logout User", success, details)
            return success
        except Exception as e:
            self.log_test("Logout User", False, f"Error: {str(e)}")
            return False

    def test_delete_book(self):
        """Test book deletion"""
        if not self.created_book_id:
            self.log_test("Delete Book", False, "No book ID available")
            return False
        
        try:
            response = self.session.delete(f"{self.api_url}/books/{self.created_book_id}", timeout=10)
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
        print("🚀 Starting GlasEditionsLab API Tests")
        print(f"📡 Testing API at: {self.api_url}")
        print("=" * 60)
        
        # Core API tests
        self.test_api_root()
        
        # Test subscription plans (no auth required)
        print("\n💳 Testing Subscription Plans...")
        self.test_get_plans()
        
        # Authentication tests
        print("\n🔐 Testing Authentication Features...")
        auth_success = self.test_register_user()
        if not auth_success:
            # Try login with existing credentials
            print("Registration failed, trying login with existing credentials...")
            auth_success = self.test_login_user()
        
        if auth_success:
            self.test_get_current_user()
        else:
            print("⚠️ Authentication failed - some tests may not work properly")
        
        # Book management tests
        print("\n📚 Testing Book Management...")
        self.test_create_book()
        self.test_get_books()
        self.test_get_book_by_id()
        
        # Test book title update
        if self.created_book_id:
            self.test_book_title_update()
        
        # AI Generation tests (these may take time)
        print("\n🤖 Testing AI Generation Features...")
        self.test_generate_outline()
        
        # Wait for outline to be ready before testing other features
        if self.created_book_id:
            print("⏳ Waiting for outline generation to complete...")
            for i in range(15):  # Wait up to 45 seconds
                time.sleep(3)
                try:
                    response = self.session.get(f"{self.api_url}/books/{self.created_book_id}")
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
        
        # Test cover generation
        print("\n🎨 Testing Cover Generation...")
        self.test_generate_cover()
        
        # Test chapter generation (start process only)
        self.test_generate_all_chapters()
        
        # Test chapter regeneration
        self.test_regenerate_chapter()
        
        # Export tests
        print("\n📄 Testing Export Features...")
        self.test_export_txt()
        self.test_export_html()
        self.test_export_pdf()
        
        # Authentication cleanup
        print("\n🔐 Testing Logout...")
        if self.auth_token:
            self.test_logout_user()
        
        # Cleanup
        print("\n🧹 Cleanup...")
        self.test_delete_book()
        
        # Results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        # Save detailed results
        results_file = f"/app/test_reports/backend_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(results_file, 'w') as f:
                json.dump({
                    "summary": {
                        "total_tests": self.tests_run,
                        "passed_tests": self.tests_passed,
                        "success_rate": round((self.tests_passed / self.tests_run) * 100, 2) if self.tests_run > 0 else 0,
                        "timestamp": datetime.now().isoformat()
                    },
                    "test_results": self.test_results
                }, f, indent=2)
            print(f"📋 Detailed results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️ Could not save results file: {e}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed. Check details above.")
            return 1

def main():
    tester = GlasEditionsLabAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())