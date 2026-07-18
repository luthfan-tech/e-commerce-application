# 🛒 ShopHub - Multi-Vendor E-Commerce Platform

A modern, asynchronous e-commerce platform built with **FastAPI**, **SQLAlchemy 2.0**, and **Vanilla JavaScript**. Complete with customer storefront, seller portal, shopping cart, checkout, and order management.

## 📋 Architecture Overview

The application follows a **three-layer architecture** pattern:

### 1. **database.py** - The Async Data Layer
- Async SQLAlchemy 2.0 with AIOSQLITE
- Database models: User, Product, CartItem, Order, OrderItem
- Async query helpers for efficient database operations
- Password hashing with bcrypt

### 2. **templates/ & static/** - The Stealth Frontend
- Responsive HTML/CSS templates
- `index.html` - Customer Hub with product browsing and shopping
- `admin.html` - Seller Portal with product management
- `app.js` - Frontend controller handling all client-side logic

### 3. **main.py** - The FastAPI Application Brain
- RESTful API endpoints for all operations
- JWT authentication and session management
- Business logic for cart, checkout, and inventory
- SMS receipt notifications (simulated)
- Async request processing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python main.py
```

The application will start at `http://localhost:8000`

### Directory Structure
```
.
├── main.py              # FastAPI application
├── database.py          # SQLAlchemy models & async database layer
├── requirements.txt     # Python dependencies
├── templates/
│   ├── index.html       # Customer Hub
│   └── admin.html       # Seller Portal
├── static/
│   └── app.js          # Frontend JavaScript controller
└── ecommerce.db        # SQLite database (auto-created)
```

## 🎯 Features

### Customer Features
- ✅ User Registration & Login with JWT authentication
- ✅ Product browsing with category filtering
- ✅ Shopping cart with add/remove items
- ✅ Secure checkout with inventory verification
- ✅ Order history and status tracking
- ✅ SMS receipt notifications (simulated)

### Seller Features
- ✅ Product upload and management
- ✅ Real-time inventory updates
- ✅ Order management and status updates
- ✅ Sales analytics and dashboard
- ✅ Revenue tracking

### Admin Features
- ✅ Order status management
- ✅ Product verification
- ✅ System health monitoring

## 🔐 Authentication

**JWT-based authentication** with secure password hashing:
- Username and password required for registration
- Session tokens stored as HTTP-only cookies
- Automatic token expiration (7 days)

### Credentials
For testing, register new accounts through the UI:
1. Click "Login"
2. Check "Create new account"
3. Enter username, password, and optional mobile number

## 📡 API Endpoints

### Authentication
```
POST   /api/auth/register    # Register new user
POST   /api/auth/login       # Login user
POST   /api/auth/logout      # Logout user
GET    /api/users/me         # Get current user info
```

### Products
```
GET    /api/products         # List all products
GET    /api/products/{id}    # Get product details
POST   /api/products         # Create product (seller)
```

### Cart
```
GET    /api/cart             # Get cart items
POST   /api/cart/add         # Add to cart
DELETE /api/cart/{id}        # Remove from cart
POST   /api/cart/clear       # Clear entire cart
```

### Orders
```
POST   /api/checkout         # Create order from cart
GET    /api/orders           # Get user's orders
GET    /api/orders/{id}      # Get order details
PUT    /api/orders/{id}/status # Update order status
```

### Utility
```
GET    /health               # Health check
```

## 💾 Database Schema

### Users Table
```
- id (PK)
- username (unique)
- hashed_password
- mobile
- role (customer/seller/admin)
- created_at
```

### Products Table
```
- id (PK)
- name
- description
- category
- price
- stock
- image_path
- seller_id (FK)
- created_at
- updated_at
```

### Cart Items Table
```
- id (PK)
- user_id (FK)
- product_id (FK)
- quantity
- added_at
```

### Orders Table
```
- id (PK)
- user_id (FK)
- total_price
- timestamp
- user_mobile
- status (pending/confirmed/shipped/delivered)
- created_at
```

### Order Items Table
```
- id (PK)
- order_id (FK)
- product_id (FK)
- quantity
- price_at_purchase
```

## 🛠️ Development

### Adding Sample Data

```python
# Create sample user
user = User(username="seller1", mobile="9876543210")
user.set_password("password123")
session.add(user)

# Create sample product
product = Product(
    name="Wireless Headphones",
    description="High-quality audio",
    category="Electronics",
    price=2999.99,
    stock=50,
    seller_id=1
)
session.add(product)
await session.commit()
```

### Customization

1. **Change Database**: Update `DATABASE_URL` in `database.py`
2. **Modify JWT Secret**: Update `SECRET_KEY` in `main.py`
3. **Update Styling**: Edit CSS in `index.html` and `admin.html`
4. **Add SMS Provider**: Integrate Twilio or AWS SNS in `send_sms_receipt()`

## 📊 Testing the Platform

### Customer Flow
1. Navigate to `http://localhost:8000`
2. Click "Login" → "Create new account"
3. Register with username and password
4. Browse products and add to cart
5. Click cart icon → "Proceed to Checkout"
6. View orders in "My Orders" section

### Seller Flow
1. Navigate to `http://localhost:8000/admin`
2. Login with seller account (register with seller role)
3. Upload products in "Upload Product" tab
4. View orders and manage inventory
5. Update order status as items are processed

## 🔄 Async Architecture Benefits

- **Non-blocking I/O**: Handles multiple simultaneous requests
- **Database Efficiency**: Async SQLAlchemy queries
- **Scalability**: Can handle high concurrent users
- **Performance**: Reduced latency and resource usage

## 📈 Performance Optimization

- Connection pooling for database
- Indexed queries on frequently searched fields
- Async route handlers
- Efficient stock verification
- Response caching possibilities

## 🚨 Security Features

✅ **Password Security**
- Bcrypt hashing with automatic salt generation
- Never store plain passwords

✅ **Authentication**
- JWT tokens with expiration
- HTTP-only cookie storage
- Session validation on protected routes

✅ **API Security**
- CORS configuration (configure as needed)
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM

✅ **Data Protection**
- Role-based access control (customer/seller/admin)
- User can only access their own data
- Seller can only manage their products

## 🐛 Troubleshooting

### Database Lock Issues
```python
# SQLite can have locking issues. Use WAL mode:
# Add to DATABASE_URL: ?timeout=20
DATABASE_URL = "sqlite+aiosqlite:///./ecommerce.db?timeout=20"
```

### CORS Issues
If accessing from different domain, add:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Port Already in Use
```bash
# Run on different port
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

## 📦 Production Deployment

Before deploying to production:

1. **Change SECRET_KEY** in `main.py`
2. **Use PostgreSQL** instead of SQLite:
   ```python
   DATABASE_URL = "postgresql+asyncpg://user:password@localhost/shopdb"
   ```
3. **Enable HTTPS** with SSL certificates
4. **Set up proper logging**
5. **Configure environment variables**
6. **Use production ASGI server**: Gunicorn with Uvicorn workers
7. **Set up database backups**
8. **Configure real SMS provider**

### Production ASGI Server Setup
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn |
| Database | SQLAlchemy 2.0, AIOSQLITE |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Auth | JWT, bcrypt |
| Async | Python asyncio, async/await |

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Feel free to fork and submit pull requests for improvements!

## 📞 Support

For issues or questions, refer to:
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Async: https://docs.sqlalchemy.org/asyncio
- Uvicorn: https://www.uvicorn.org

---

**Built with ⚡ FastAPI + 🗄️ SQLAlchemy + 🎨 Vanilla JS**

Happy coding! 🚀
