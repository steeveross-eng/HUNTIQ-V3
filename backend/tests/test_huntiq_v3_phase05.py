"""
HUNTIQ V3 Phase 0.5 - Comprehensive API Tests
Tests for: Freemium Engine, Onboarding Engine, Tutorials Engine, Admin Users, Payment Engine
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://huntiq-merge.preview.emergentagent.com').rstrip('/')

class TestAPIRoot:
    """Test API Root endpoint"""
    
    def test_api_root_returns_welcome_message(self):
        """Test /api/ returns welcome message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Chasse Bionic" in data["message"] or "API" in data["message"]


class TestFreemiumEngine:
    """Freemium Engine - Quota management tests"""
    
    def test_freemium_status_for_user(self):
        """Test /api/freemium/status/{user_id} - check user PRO status"""
        response = requests.get(f"{BASE_URL}/api/freemium/status/test_user_123")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "is_pro" in data
        assert "pro_type" in data
        assert "days_remaining" in data
        assert data["user_id"] == "test_user_123"
        assert isinstance(data["is_pro"], bool)
    
    def test_freemium_check_quota(self):
        """Test /api/freemium/check - validate quota system"""
        response = requests.post(
            f"{BASE_URL}/api/freemium/check",
            json={"user_id": "test_user_123", "feature": "analyzer_ai"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "feature" in data
        assert "allowed" in data
        assert "used" in data
        assert "limit" in data
        assert "remaining" in data
        assert "is_pro" in data
        assert data["feature"] == "analyzer_ai"
        assert isinstance(data["allowed"], bool)
    
    def test_freemium_quotas_config(self):
        """Test /api/freemium/quotas - get quotas configuration"""
        response = requests.get(f"{BASE_URL}/api/freemium/quotas")
        assert response.status_code == 200
        data = response.json()
        assert "free_quotas" in data
        assert "pro_features" in data
        assert "pricing" in data
        
        # Validate FREE quotas
        free_quotas = data["free_quotas"]
        assert "marketplace_listings" in free_quotas
        assert "analyzer_ai" in free_quotas
        assert "territories" in free_quotas
        assert "waypoints" in free_quotas
        
        # Validate quota limits
        assert free_quotas["marketplace_listings"]["limit"] == 2
        assert free_quotas["analyzer_ai"]["limit"] == 1
        assert free_quotas["territories"]["limit"] == 1
        assert free_quotas["waypoints"]["limit"] == 2
        
        # Validate PRO pricing (7.99/79/199 CAD)
        pricing = data["pricing"]
        assert pricing["monthly"]["amount"] == 7.99
        assert pricing["yearly"]["amount"] == 79.0
        assert pricing["lifetime"]["amount"] == 199.0
        assert pricing["monthly"]["currency"] == "CAD"
    
    def test_freemium_user_quotas(self):
        """Test /api/freemium/user/{user_id} - get user quotas"""
        response = requests.get(f"{BASE_URL}/api/freemium/user/test_user_123")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "is_pro" in data
        assert "quotas" in data


class TestOnboardingEngine:
    """Onboarding Engine - User onboarding flow tests"""
    
    def test_onboarding_config(self):
        """Test /api/onboarding/config - get configuration"""
        response = requests.get(f"{BASE_URL}/api/onboarding/config")
        assert response.status_code == 200
        data = response.json()
        assert "steps" in data
        assert "options" in data
        
        # Validate 5 onboarding steps
        steps = data["steps"]
        assert len(steps) == 5
        step_ids = [s["id"] for s in steps]
        assert "welcome" in step_ids
        assert "profile" in step_ids
        assert "preferences" in step_ids
        assert "features" in step_ids
        assert "complete" in step_ids
        
        # Validate options
        options = data["options"]
        assert "target_species" in options
        assert "regions" in options
        assert "experience_levels" in options
        assert "hunting_objectives" in options
        
        # Validate 8 target species
        assert len(options["target_species"]) == 8
        
        # Validate 16 Quebec regions
        assert len(options["regions"]) == 16
    
    def test_onboarding_progress(self):
        """Test /api/onboarding/progress/{user_id} - get/create user progress"""
        response = requests.get(f"{BASE_URL}/api/onboarding/progress/test_user_123")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "current_step" in data
        assert "completed_steps" in data
        assert "is_complete" in data
    
    def test_onboarding_step_complete(self):
        """Test /api/onboarding/step/complete - complete a step"""
        # First, get progress to ensure user exists in onboarding
        progress_response = requests.get(f"{BASE_URL}/api/onboarding/progress/test_user_step_complete")
        assert progress_response.status_code == 200
        
        # Now complete a step
        response = requests.post(
            f"{BASE_URL}/api/onboarding/step/complete",
            json={
                "user_id": "test_user_step_complete",
                "step_id": "welcome",
                "data": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "completed_step" in data or "message" in data


class TestTutorialsEngine:
    """Tutorials Engine - Interactive tutorials tests"""
    
    def test_tutorials_list(self):
        """Test /api/tutorials/list - get all tutorials"""
        response = requests.get(f"{BASE_URL}/api/tutorials/list")
        assert response.status_code == 200
        data = response.json()
        assert "tutorials" in data
        assert "categories" in data
        
        # Validate 3 core tutorials
        tutorials = data["tutorials"]
        assert len(tutorials) >= 3
        
        tutorial_ids = [t["id"] for t in tutorials]
        assert "analyzer_bionic" in tutorial_ids
        assert "territory_map" in tutorial_ids
        assert "marketplace" in tutorial_ids
    
    def test_tutorials_detail(self):
        """Test /api/tutorials/detail/{tutorial_id} - get tutorial details"""
        response = requests.get(f"{BASE_URL}/api/tutorials/detail/analyzer_bionic")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "description" in data
        assert "steps" in data
        
        assert data["id"] == "analyzer_bionic"
        assert data["title"] == "Analyzer BIONIC™"
        assert len(data["steps"]) == 5
    
    def test_tutorials_progress(self):
        """Test /api/tutorials/progress/{user_id} - get user tutorial progress"""
        response = requests.get(f"{BASE_URL}/api/tutorials/progress/test_user_123")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "tutorials" in data
        assert "total_tutorials" in data
        assert "completed_tutorials" in data


class TestAdminUsersModule:
    """Admin Users Module - Top users management tests"""
    
    def test_admin_users_top(self):
        """Test /api/admin/users/top - get top users by category"""
        response = requests.get(f"{BASE_URL}/api/admin/users/top")
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "users" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data
    
    def test_admin_users_top_categories(self):
        """Test /api/admin/users/top/categories - get all categories"""
        response = requests.get(f"{BASE_URL}/api/admin/users/top/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        
        # Validate 12 categories
        categories = data["categories"]
        assert len(categories) == 12
        
        category_ids = [c["id"] for c in categories]
        expected_categories = [
            "global", "free", "pro_monthly", "pro_yearly", "pro_lifetime",
            "contributors", "marketplace", "analyzer", "territory", "growth",
            "pro_boost_candidates", "mastery_candidates"
        ]
        for cat in expected_categories:
            assert cat in category_ids, f"Missing category: {cat}"
    
    def test_admin_stats(self):
        """Test /api/admin/stats - get dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert "products_count" in data
        assert "suppliers_count" in data
        assert "customers_count" in data
        assert "orders_count" in data
        assert "orders_by_status" in data
        assert "total_sales" in data
    
    def test_admin_users_stats_summary(self):
        """Test /api/admin/users/stats/summary - get users summary"""
        response = requests.get(f"{BASE_URL}/api/admin/users/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "free_users" in data
        assert "pro_users" in data
        assert "conversion_rate" in data


class TestProductsCRUD:
    """Products CRUD - Product management tests"""
    
    def test_products_list(self):
        """Test /api/products - list products"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_products_top(self):
        """Test /api/products/top - get top products"""
        response = requests.get(f"{BASE_URL}/api/products/top?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_products_create(self):
        """Test /api/products - create product"""
        product_data = {
            "name": "TEST_Product_Attractant",
            "brand": "Test Brand",
            "price": 29.99,
            "score": 85,
            "rank": 999,
            "image_url": "https://example.com/test.jpg",
            "description": "Test product for API testing",
            "category": "attractant"
        }
        response = requests.post(f"{BASE_URL}/api/products", json=product_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "TEST_Product_Attractant"
        assert data["price"] == 29.99


class TestPaymentEngine:
    """Payment Engine - Stripe payment integration tests"""
    
    def test_payment_packages(self):
        """Test /api/payments/packages - get PRO plans"""
        response = requests.get(f"{BASE_URL}/api/payments/packages")
        assert response.status_code == 200
        data = response.json()
        assert "packages" in data
        assert "categories" in data
        
        packages = data["packages"]
        
        # Find PRO packages
        pro_monthly = next((p for p in packages if p["id"] == "pro_monthly"), None)
        pro_yearly = next((p for p in packages if p["id"] == "pro_yearly"), None)
        pro_lifetime = next((p for p in packages if p["id"] == "pro_lifetime"), None)
        
        # Validate PRO pricing (7.99/79/199 CAD)
        assert pro_monthly is not None
        assert pro_monthly["amount"] == 7.99
        assert pro_monthly["currency"] == "cad"
        
        assert pro_yearly is not None
        assert pro_yearly["amount"] == 79.0
        assert pro_yearly["currency"] == "cad"
        
        assert pro_lifetime is not None
        assert pro_lifetime["amount"] == 199.0
        assert pro_lifetime["currency"] == "cad"


class TestSiteStatus:
    """Site Status - Maintenance mode tests"""
    
    def test_site_status(self):
        """Test /api/site/status - get site maintenance status"""
        response = requests.get(f"{BASE_URL}/api/site/status")
        assert response.status_code == 200
        data = response.json()
        assert "maintenance_mode" in data
        assert "maintenance_title" in data
        assert "maintenance_message" in data
        assert isinstance(data["maintenance_mode"], bool)


class TestAdminLogin:
    """Admin Authentication tests"""
    
    def test_admin_login_success(self):
        """Test /api/admin/login - successful login"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"password": "Saturn5858*"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] == True
    
    def test_admin_login_failure(self):
        """Test /api/admin/login - failed login"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"password": "wrong_password"}
        )
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
