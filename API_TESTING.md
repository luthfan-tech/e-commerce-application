# 🧪 ShopHub API Testing Guide

Complete guide for testing the ShopHub API using curl, Postman, or Python.

## Quick Start

### 1. Start the Application
```bash
python main.py
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 2. Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "database": "connected"
}
```

---

## API Endpoints Testing

### Authentication

#### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!",
    "mobile": "9876543210",
    "role": "customer"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

This saves the authentication cookie to `cookies.txt`.

#### Get Current User
```bash
curl http://localhost:8000/api/users/me \
  -b cookies.txt
```

#### Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -b cookies.txt
```

---

### Products

#### List All Products
```bash
curl http://localhost:8000/api/products
```

#### List Products by Category
```bash
curl "http://localhost:8000/api/products?category=Electronics"
```

#### Get Specific Product
```bash
curl http://localhost:8000/api/products/1
```

#### Create Product (Seller Only)
```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse with 2.4GHz connection",
    "category": "Electronics",
    "price": 599.99,
    "stock": 100,
    "image_path": "https://example.com/mouse.jpg"
  }'
```

---

### Shopping Cart

#### Get Cart Items
```bash
curl http://localhost:8000/api/cart \
  -b cookies.txt
```

#### Add Item to Cart
```bash
curl -X POST http://localhost:8000/api/cart/add \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

#### Remove Item from Cart
```bash
curl -X DELETE http://localhost:8000/api/cart/1 \
  -b cookies.txt
```

#### Clear Entire Cart
```bash
curl -X POST http://localhost:8000/api/cart/clear \
  -b cookies.txt
```

---

### Orders & Checkout

#### Checkout (Create Order)
```bash
curl -X POST http://localhost:8000/api/checkout \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{}'
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "total_price": 1199.98,
  "timestamp": "2024-01-15T10:30:00",
  "user_mobile": "9876543210",
  "status": "pending",
  "order_items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "price_at_purchase": 599.99
    }
  ]
}
```

#### Get User's Orders
```bash
curl http://localhost:8000/api/orders \
  -b cookies.txt
```

#### Get Specific Order
```bash
curl http://localhost:8000/api/orders/1 \
  -b cookies.txt
```

#### Update Order Status (Admin/Seller Only)
```bash
curl -X PUT http://localhost:8000/api/orders/1/status \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"status": "confirmed"}'
```

Valid statuses: `pending`, `confirmed`, `shipped`, `delivered`

---

## Testing with Postman

### 1. Import Collection

Create a new Postman collection:

1. Open Postman
2. Click "Import" → "Link"
3. Use this URL or manually create collections

### 2. Environment Variables

Create a new environment with:
```json
{
  "base_url": "http://localhost:8000",
  "username": "john_doe",
  "password": "SecurePass123!",
  "product_id": 1,
  "order_id": 1
}
```

### 3. Collection Structure

```
ShopHub API
├── Auth
│   ├── Register
│   ├── Login
│   ├── Logout
│   └── Get User
├── Products
│   ├── List All
│   ├── Get by Category
│   ├── Get One
│   └── Create
├── Cart
│   ├── Get Items
│   ├── Add Item
│   ├── Remove Item
│   └── Clear Cart
└── Orders
    ├── Checkout
    ├── Get Orders
    ├── Get One
    └── Update Status
```

---

## Testing with Python

### Using Requests Library

```python
import requests
import json

BASE_URL = "http://localhost:8000"
session = requests.Session()

# Register
print("=== Testing Registration ===")
response = session.post(f"{BASE_URL}/api/auth/register", json={
    "username": "alice_smith",
    "password": "Password123!",
    "mobile": "9123456789",
    "role": "customer"
})
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Login
print("\n=== Testing Login ===")
response = session.post(f"{BASE_URL}/api/auth/login", json={
    "username": "alice_smith",
    "password": "Password123!"
})
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Get Products
print("\n=== Testing Get Products ===")
response = session.get(f"{BASE_URL}/api/products")
products = response.json()
print(f"Found {len(products)} products")
if products:
    product_id = products[0]["id"]
    print(f"First product ID: {product_id}")

# Add to Cart
print("\n=== Testing Add to Cart ===")
response = session.post(f"{BASE_URL}/api/cart/add", json={
    "product_id": product_id,
    "quantity": 2
})
print(f"Status: {response.status_code}")
print(response.json())

# Get Cart
print("\n=== Testing Get Cart ===")
response = session.get(f"{BASE_URL}/api/cart")
cart_items = response.json()
print(f"Cart items: {len(cart_items)}")
print(json.dumps(cart_items[:1], indent=2))  # Show first item

# Checkout
print("\n=== Testing Checkout ===")
response = session.post(f"{BASE_URL}/api/checkout", json={})
print(f"Status: {response.status_code}")
order = response.json()
print(json.dumps(order, indent=2, default=str))

# Get Orders
print("\n=== Testing Get Orders ===")
response = session.get(f"{BASE_URL}/api/orders")
orders = response.json()
print(f"Total orders: {len(orders)}")

# Logout
print("\n=== Testing Logout ===")
response = session.post(f"{BASE_URL}/api/auth/logout")
print(f"Status: {response.status_code}")
print(response.json())
```

### Using pytest

Create `test_api.py`:

```python
import pytest
import requests

BASE_URL = "http://localhost:8000"

@pytest.fixture
def client():
    """Create a requests session for testing"""
    return requests.Session()

class TestAuth:
    def test_register(self, client):
        response = client.post(f"{BASE_URL}/api/auth/register", json={
            "username": "testuser",
            "password": "testpass123",
            "role": "customer"
        })
        assert response.status_code == 200
        assert "id" in response.json()

    def test_login(self, client):
        response = client.post(f"{BASE_URL}/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

class TestProducts:
    def test_list_products(self, client):
        response = client.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_filter_by_category(self, client):
        response = client.get(f"{BASE_URL}/api/products?category=Electronics")
        assert response.status_code == 200
        products = response.json()
        assert all(p["category"] == "Electronics" for p in products)

class TestCart:
    def test_add_to_cart(self, client):
        # First get a product
        products = client.get(f"{BASE_URL}/api/products").json()
        
        # Login
        client.post(f"{BASE_URL}/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        # Add to cart
        response = client.post(f"{BASE_URL}/api/cart/add", json={
            "product_id": products[0]["id"],
            "quantity": 1
        })
        assert response.status_code == 200

class TestOrders:
    def test_checkout(self, client):
        # Login, add item, then checkout
        client.post(f"{BASE_URL}/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        products = client.get(f"{BASE_URL}/api/products").json()
        
        client.post(f"{BASE_URL}/api/cart/add", json={
            "product_id": products[0]["id"],
            "quantity": 1
        })
        
        response = client.post(f"{BASE_URL}/api/checkout")
        assert response.status_code == 200
        assert "id" in response.json()  # Order ID

# Run tests
# pytest test_api.py -v
```

Run tests:
```bash
pip install pytest
pytest test_api.py -v
```

---

## Load Testing with Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between
import random

class ShopHubUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login at start"""
        self.client.post("/api/auth/register", json={
            "username": f"user_{random.randint(1000, 9999)}",
            "password": "testpass123"
        })
        
        self.client.post("/api/auth/login", json={
            "username": f"user_{random.randint(1000, 9999)}",
            "password": "testpass123"
        })

    @task(3)
    def browse_products(self):
        """Browse products"""
        self.client.get("/api/products")
        
        categories = ["Electronics", "Clothing", "Books", "Home"]
        self.client.get(f"/api/products?category={random.choice(categories)}")

    @task(1)
    def add_to_cart(self):
        """Add item to cart"""
        product_id = random.randint(1, 10)
        self.client.post("/api/cart/add", json={
            "product_id": product_id,
            "quantity": random.randint(1, 3)
        })

    @task(1)
    def checkout(self):
        """Complete checkout"""
        self.client.post("/api/checkout")

    @task(1)
    def view_orders(self):
        """View orders"""
        self.client.get("/api/orders")
```

Run load test:
```bash
pip install locust

# Interactive mode
locust -f locustfile.py --host=http://localhost:8000

# Headless mode
locust -f locustfile.py --host=http://localhost:8000 \
    -u 100 -r 10 -t 5m --headless
```

Then open: `http://localhost:8089`

---

## Error Response Examples

### 401 Unauthorized
```bash
curl http://localhost:8000/api/cart
```

Response:
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```bash
curl http://localhost:8000/api/products/999
```

Response:
```json
{
  "detail": "Product not found"
}
```

### 400 Bad Request
```bash
curl -X POST http://localhost:8000/api/checkout -b cookies.txt
```

Response (empty cart):
```json
{
  "detail": "Cart is empty"
}
```

### 403 Forbidden
```bash
curl -X POST http://localhost:8000/api/products -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"name": "Product"}'
```

Response (customer trying to create product):
```json
{
  "detail": "Only sellers can create products"
}
```

---

## Performance Benchmarks

### Expected Response Times
- List products: < 100ms
- Get single product: < 50ms
- Add to cart: < 200ms
- Checkout: < 500ms
- Search/filter: < 200ms

### Database Queries
- Optimize frequently accessed queries
- Use indexes on: `username`, `category`, `status`
- Connection pooling enabled by default

---

## Debugging Tips

### 1. Enable Verbose Logging
```bash
# In main.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Database Query Logging
```bash
# In database.py:
engine = create_async_engine(
    DATABASE_URL,
    echo=True  # Log all SQL queries
)
```

### 3. Request/Response Logging with curl
```bash
curl -v http://localhost:8000/api/products
# -v shows request/response headers
# -i shows response headers
# -d shows body
```

### 4. Check Database Directly
```bash
sqlite3 ecommerce.db
SELECT * FROM products;
SELECT * FROM cart_items;
```

---

**Last Updated:** 2024
**Version:** 1.0.0
