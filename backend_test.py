import requests
import sys
from datetime import datetime

class HuntiqAPITester:
    def __init__(self, base_url="https://terra-analysis-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = f"test_session_{datetime.now().strftime('%H%M%S')}"

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if len(response_data) > 0:
                            print(f"   First item keys: {list(response_data[0].keys()) if response_data[0] else 'Empty'}")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    print(f"   Response: Non-JSON or empty")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_products_top(self):
        """Test top products endpoint (should return 5 seeded products)"""
        success, response = self.run_test("Top Products", "GET", "products/top", 200, params={"limit": 10})
        if success and isinstance(response, list):
            print(f"   Found {len(response)} products")
            for i, product in enumerate(response[:3]):  # Show first 3 products
                print(f"   Product {i+1}: {product.get('name', 'Unknown')} - Rank: {product.get('rank', 'N/A')} - Price: ${product.get('price', 'N/A')}")
        return success, response

    def test_all_products(self):
        """Test all products endpoint"""
        return self.run_test("All Products", "GET", "products", 200)

    def test_product_filters(self):
        """Test product filter options"""
        return self.run_test("Product Filter Options", "GET", "products/filters/options", 200)

    def test_cart_functionality(self):
        """Test cart add functionality"""
        # First get a product to add to cart
        success, products = self.test_products_top()
        if not success or not products:
            print("❌ Cannot test cart - no products available")
            return False, {}
        
        product_id = products[0].get('id')
        if not product_id:
            print("❌ Cannot test cart - no product ID")
            return False, {}
        
        # Test adding to cart
        cart_data = {
            "session_id": self.session_id,
            "product_id": product_id,
            "quantity": 1
        }
        
        success, response = self.run_test("Add to Cart", "POST", "cart", 200, data=cart_data)
        if success:
            print(f"   Added product {product_id} to cart")
        
        # Test getting cart
        success2, cart_response = self.run_test("Get Cart", "GET", f"cart/{self.session_id}", 200)
        if success2:
            print(f"   Cart contains {len(cart_response) if isinstance(cart_response, list) else 0} items")
        
        return success and success2, response

    def test_site_status(self):
        """Test site status endpoint"""
        return self.run_test("Site Status", "GET", "site/status", 200)

    def test_analyze_basic(self):
        """Test basic product analysis endpoint"""
        analyze_data = {
            "product_name": "Buck Bomb Deer"
        }
        return self.run_test("Basic Analysis", "POST", "analyze", 200, data=analyze_data)

    def test_analyze_ai_advanced(self):
        """Test AI advanced analysis endpoint with GPT-5.2"""
        ai_analyze_data = {
            "product_name": "BIONIC Apple Jelly",
            "species": "cerf",
            "season": "automne",
            "weather": "normal",
            "terrain": "forêt"
        }
        success, response = self.run_test("AI Advanced Analysis", "POST", "analyze/ai-advanced", 200, data=ai_analyze_data)
        if success and isinstance(response, dict):
            print(f"   AI Analysis Score: {response.get('score', 'N/A')}")
            print(f"   Effectiveness Rating: {response.get('effectiveness_rating', 'N/A')}")
            print(f"   Species: {response.get('species', 'N/A')}")
            print(f"   Season: {response.get('season', 'N/A')}")
        return success, response

    def test_analyze_criteria(self):
        """Test analysis criteria endpoint"""
        return self.run_test("Analysis Criteria", "GET", "analyze/criteria", 200)

def main():
    print("🚀 Starting HUNTIQ V3 API Testing...")
    print("=" * 50)
    
    # Setup
    tester = HuntiqAPITester()
    
    # Run core API tests
    print("\n📋 Testing Core API Endpoints...")
    tester.test_root_endpoint()
    tester.test_site_status()
    
    print("\n🛍️ Testing Product Endpoints...")
    tester.test_products_top()
    tester.test_all_products()
    tester.test_product_filters()
    
    print("\n🛒 Testing Cart Functionality...")
    tester.test_cart_functionality()
    
    print("\n🧪 Testing Analyzer Module...")
    tester.test_analyze_criteria()
    tester.test_analyze_basic()
    tester.test_analyze_ai_advanced()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())