import pytest
import requests
import time

# Service URLs
USER_SERVICE_URL = "http://localhost:8001"
ORDER_SERVICE_URL = "http://localhost:8002"

@pytest.fixture(scope="module")
def wait_for_services():
    """Wait for services to be ready"""
    max_retries = 30
    for i in range(max_retries):
        try:
            user_health = requests.get(f"{USER_SERVICE_URL}/health", timeout=2)
            order_health = requests.get(f"{ORDER_SERVICE_URL}/health", timeout=2)
            if user_health.status_code == 200 and order_health.status_code == 200:
                print("✅ Services are ready")
                return
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(2)
    pytest.fail("Services did not start in time")

class TestUserService:
    """Test User Service endpoints"""
    
    def test_user_service_health(self, wait_for_services):
        response = requests.get(f"{USER_SERVICE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_user_by_id(self, wait_for_services):
        response = requests.get(f"{USER_SERVICE_URL}/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Alice Johnson"
        assert data["email"] == "alice@example.com"
    
    def test_get_user_not_found(self, wait_for_services):
        response = requests.get(f"{USER_SERVICE_URL}/users/999")
        assert response.status_code == 404
    
    def test_get_all_users(self, wait_for_services):
        response = requests.get(f"{USER_SERVICE_URL}/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    def test_get_active_users_only(self, wait_for_services):
        response = requests.get(f"{USER_SERVICE_URL}/users?active=true")
        assert response.status_code == 200
        data = response.json()
        assert all(user["active"] for user in data)

class TestOrderService:
    """Test Order Service endpoints"""
    
    def test_order_service_health(self, wait_for_services):
        response = requests.get(f"{ORDER_SERVICE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_order_by_id(self, wait_for_services):
        response = requests.get(f"{ORDER_SERVICE_URL}/orders/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["product"] == "Laptop"
    
    def test_get_all_orders(self, wait_for_services):
        response = requests.get(f"{ORDER_SERVICE_URL}/orders")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

class TestIntegration:
    """Test integration between services"""
    
    def test_order_includes_user_details(self, wait_for_services):
        """Order service should call User service to get user details"""
        response = requests.get(f"{ORDER_SERVICE_URL}/orders/1")
        assert response.status_code == 200
        data = response.json()
        
        # Order data
        assert data["id"] == 1
        assert data["user_id"] == 1
        
        # User data from User Service
        assert "user" in data
        assert data["user"]["id"] == 1
        assert data["user"]["name"] == "Alice Johnson"
    
    def test_get_orders_by_user(self, wait_for_services):
        """Get all orders for a specific user"""
        response = requests.get(f"{ORDER_SERVICE_URL}/orders/user/1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(order["user_id"] == 1 for order in data)
    
    def test_create_order_for_valid_user(self, wait_for_services):
        """Create order for existing active user"""
        new_order = {
            "user_id": 1,
            "product": "Monitor",
            "quantity": 1,
            "total": 300.00
        }
        response = requests.post(f"{ORDER_SERVICE_URL}/orders", json=new_order)
        assert response.status_code == 201
        data = response.json()
        assert data["product"] == "Monitor"
        assert data["user_id"] == 1
        assert data["status"] == "pending"
    
    def test_create_order_for_inactive_user(self, wait_for_services):
        """Cannot create order for inactive user"""
        new_order = {
            "user_id": 3,  # Charlie is inactive
            "product": "Headphones",
            "quantity": 1,
            "total": 100.00
        }
        response = requests.post(f"{ORDER_SERVICE_URL}/orders", json=new_order)
        assert response.status_code == 400
        assert "not active" in response.json()["error"].lower()
    
    def test_create_order_for_nonexistent_user(self, wait_for_services):
        """Cannot create order for non-existent user"""
        new_order = {
            "user_id": 999,
            "product": "Phone",
            "quantity": 1,
            "total": 800.00
        }
        response = requests.post(f"{ORDER_SERVICE_URL}/orders", json=new_order)
        assert response.status_code == 404
        
        