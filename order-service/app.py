from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# Configuration
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

# In-memory database
orders_db = {
    1: {"id": 1, "user_id": 1, "product": "Laptop", "quantity": 1, "total": 1200.00, "status": "completed"},
    2: {"id": 2, "user_id": 1, "product": "Mouse", "quantity": 2, "total": 50.00, "status": "pending"},
    3: {"id": 3, "user_id": 2, "product": "Keyboard", "quantity": 1, "total": 80.00, "status": "completed"}
}

@app.route('/')
def root():
    return jsonify({
        "service": "Order Service",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/orders/<int:order_id>')
def get_order(order_id):
    """Get order by ID with user details"""
    if order_id not in orders_db:
        return jsonify({"error": "Order not found"}), 404
    
    order = orders_db[order_id].copy()
    
    # Call User Service to get user details
    try:
        user_response = requests.get(f"{USER_SERVICE_URL}/users/{order['user_id']}", timeout=5)
        if user_response.status_code == 200:
            order['user'] = user_response.json()
        else:
            order['user'] = {"error": "User not found"}
    except requests.exceptions.RequestException as e:
        order['user'] = {"error": "User service unavailable"}
    
    return jsonify(order)

@app.route('/orders')
def get_all_orders():
    """Get all orders"""
    return jsonify(list(orders_db.values()))

@app.route('/orders/user/<int:user_id>')
def get_orders_by_user(user_id):
    """Get all orders for a specific user"""
    # First verify user exists
    try:
        user_response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}", timeout=5)
        if user_response.status_code != 200:
            return jsonify({"error": "User not found"}), 404
    except requests.exceptions.RequestException:
        return jsonify({"error": "User service unavailable"}), 503
    
    user_orders = [order for order in orders_db.values() if order['user_id'] == user_id]
    return jsonify(user_orders)

@app.route('/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    data = request.get_json()
    
    # Validate user exists
    try:
        user_response = requests.get(f"{USER_SERVICE_URL}/users/{data['user_id']}", timeout=5)
        if user_response.status_code != 200:
            return jsonify({"error": "User not found"}), 404
        
        user = user_response.json()
        if not user.get('active', False):
            return jsonify({"error": "User is not active"}), 400
            
    except requests.exceptions.RequestException:
        return jsonify({"error": "User service unavailable"}), 503
    
    # Create order
    new_id = max(orders_db.keys()) + 1 if orders_db else 1
    new_order = {
        "id": new_id,
        "user_id": data['user_id'],
        "product": data['product'],
        "quantity": data.get('quantity', 1),
        "total": data['total'],
        "status": "pending"
    }
    orders_db[new_id] = new_order
    return jsonify(new_order), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)
    