#!/usr/bin/env python3
"""
HUNTIQ V3 Backend API Testing Suite
Tests all API endpoints for the HUNTIQ platform
"""

import requests
import sys
import json
from datetime import datetime

class HuntiqAPITester:
    def __init__(self, base_url="https://global-audit-v3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        self.session.timeout = 30

    def run_test(self, name, method, endpoint, expected_status=200, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) <= 3:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    else:
                        print(f"   Response: {type(response_data).__name__}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })

            return success, response

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': str(e)
            })
            return False, None

    def test_root_api(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "/")

    def test_payments_packages(self):
        """Test payments packages endpoint"""
        success, response = self.run_test("Payments Packages", "GET", "/payments/packages")
        if success and response:
            try:
                data = response.json()
                packages = data.get('packages', [])
                
                # Check for PRO packages with correct pricing
                pro_monthly = next((p for p in packages if p.get('id') == 'pro_monthly'), None)
                pro_yearly = next((p for p in packages if p.get('id') == 'pro_yearly'), None)
                pro_lifetime = next((p for p in packages if p.get('id') == 'pro_lifetime'), None)
                
                if pro_monthly and pro_monthly.get('amount') == 7.99:
                    print(f"   ✅ PRO Monthly: {pro_monthly.get('amount')} CAD")
                else:
                    print(f"   ❌ PRO Monthly pricing incorrect: {pro_monthly.get('amount') if pro_monthly else 'Not found'}")
                
                if pro_yearly and pro_yearly.get('amount') == 79.0:
                    print(f"   ✅ PRO Yearly: {pro_yearly.get('amount')} CAD")
                else:
                    print(f"   ❌ PRO Yearly pricing incorrect: {pro_yearly.get('amount') if pro_yearly else 'Not found'}")
                
                if pro_lifetime and pro_lifetime.get('amount') == 199.0:
                    print(f"   ✅ PRO Lifetime: {pro_lifetime.get('amount')} CAD")
                else:
                    print(f"   ❌ PRO Lifetime pricing incorrect: {pro_lifetime.get('amount') if pro_lifetime else 'Not found'}")
                    
            except Exception as e:
                print(f"   ⚠️ Error parsing packages response: {e}")
        
        return success

    def test_products_endpoint(self):
        """Test products endpoint"""
        return self.run_test("Products List", "GET", "/products")

    def test_admin_stats(self):
        """Test admin statistics endpoint"""
        return self.run_test("Admin Statistics", "GET", "/admin/stats")

    def test_site_status(self):
        """Test site status endpoint"""
        return self.run_test("Site Status", "GET", "/site/status")

    def test_marketplace_categories(self):
        """Test marketplace categories"""
        return self.run_test("Marketplace Categories", "GET", "/marketplace/categories")

    def test_marketplace_listings(self):
        """Test marketplace listings"""
        return self.run_test("Marketplace Listings", "GET", "/marketplace/listings")

    def test_marketplace_stats(self):
        """Test marketplace stats"""
        return self.run_test("Marketplace Stats", "GET", "/marketplace/stats")

    def test_suppliers_endpoint(self):
        """Test suppliers endpoint"""
        return self.run_test("Suppliers List", "GET", "/suppliers")

    def test_customers_endpoint(self):
        """Test customers endpoint"""
        return self.run_test("Customers List", "GET", "/customers")

    def test_orders_endpoint(self):
        """Test orders endpoint"""
        return self.run_test("Orders List", "GET", "/orders")

    def test_commissions_endpoint(self):
        """Test commissions endpoint"""
        return self.run_test("Commissions List", "GET", "/commissions")

    def test_product_filters(self):
        """Test product filter options"""
        return self.run_test("Product Filter Options", "GET", "/products/filters/options")

    def test_top_products(self):
        """Test top products endpoint"""
        return self.run_test("Top Products", "GET", "/products/top?limit=5")

    def test_email_status(self):
        """Test email service status"""
        return self.run_test("Email Service Status", "GET", "/email/status")

    def test_payment_transactions(self):
        """Test payment transactions endpoint"""
        return self.run_test("Payment Transactions", "GET", "/payments/transactions")

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("🚀 HUNTIQ V3 Backend API Testing Suite")
        print("=" * 60)
        print(f"Testing API: {self.api_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Core API Tests
        print("\n📋 CORE API TESTS")
        print("-" * 30)
        self.test_root_api()
        self.test_site_status()
        self.test_email_status()
        
        # Payment Engine Tests
        print("\n💳 PAYMENT ENGINE TESTS")
        print("-" * 30)
        self.test_payments_packages()
        self.test_payment_transactions()
        
        # Product System Tests
        print("\n📦 PRODUCT SYSTEM TESTS")
        print("-" * 30)
        self.test_products_endpoint()
        self.test_top_products()
        self.test_product_filters()
        
        # Marketplace Tests
        print("\n🏪 MARKETPLACE TESTS")
        print("-" * 30)
        self.test_marketplace_categories()
        self.test_marketplace_listings()
        self.test_marketplace_stats()
        
        # Business Logic Tests
        print("\n🏢 BUSINESS LOGIC TESTS")
        print("-" * 30)
        self.test_suppliers_endpoint()
        self.test_customers_endpoint()
        self.test_orders_endpoint()
        self.test_commissions_endpoint()
        
        # Admin Tests
        print("\n👑 ADMIN TESTS")
        print("-" * 30)
        self.test_admin_stats()
        
        # Print Results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            print("-" * 30)
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['name']}")
                if 'expected' in test:
                    print(f"   Expected: {test['expected']}, Got: {test['actual']}")
                if 'error' in test:
                    print(f"   Error: {test['error']}")
                if 'response' in test:
                    print(f"   Response: {test['response'][:100]}...")
                print()
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = HuntiqAPITester()
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())