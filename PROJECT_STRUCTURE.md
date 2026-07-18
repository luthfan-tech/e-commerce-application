# 📁 ShopHub Project Structure

Complete guide to all files and folders in the ShopHub project.

## 🎯 Quick Overview

```
shopHub/
├── 📄 main.py                 # FastAPI Application (Core)
├── 📄 database.py             # SQLAlchemy Models & Async DB Layer
├── 📄 requirements.txt        # Python Dependencies
├── 📁 templates/
│   ├── index.html            # Customer Hub Frontend
│   └── admin.html            # Seller Portal Frontend
├── 📁 static/
│   └── app.js                # Frontend JavaScript Controller
├── 📄 README.md              # Main Documentation
├── 📄 DEPLOYMENT.md          # Deployment Guide
├── 📄 API_TESTING.md         # API Testing Guide
├── 📄 PROJECT_STRUCTURE.md   # This File
├── 📄 .env.example           # Environment Configuration Template
├── 📄 setup.sh               # Linux/macOS Setup Script
├── 📄 setup.bat              # Windows Setup Script
└── 📄 ecommerce.db           # SQLite Database (Auto-created)
```

---

## 📄 Core Application Files

### 1. **main.py** - FastAPI Application Brain
**Purpose:** Main application server with all API endpoints and business logic

**Sections:**
- Configuration & Settings
- Pydantic Models (API Schemas)
- Authentication & JWT
- FastAPI Application Setup
- Auth Routes (register, login, logout)
- User Routes
- Product Routes (list, get, create)
- Cart Routes (add, remove, clear)
- Checkout & Order Routes
- Frontend Routes (HTML serving)
- Health Check
- Error Handlers

**Key Dependencies:**
- FastAPI
- SQLAlchemy
- PyJWT
- Passlib

**How to Run:**
```bash
python main.py
```

**Port:** 8000

---

### 2. **database.py** - Async Data Layer
**Purpose:** Database models, async session management, and query helpers

**Sections:**
- Configuration (Database URL, Password hashing)
- Database Models:
  - `User` - Customer/Seller accounts
  - `Product` - Product catalog
  - `CartItem` - Shopping cart items
  - `Order` - Order records
  - `OrderItem` - Items within an order
- Async Database Manager (initialization, session creation)
- Database Query Helpers

**Key Features:**
- SQLAlchemy 2.0 with Async Support
- AIOSQLITE for SQLite async operations
- Bcrypt password hashing
- Relationship mapping between models
- Async helper functions for common queries

**Models Overview:**
```
User
  ├── products (1:N) → Product.seller
  ├── cart_items (1:N) → CartItem.user
  └── orders (1:N) → Order.user

Product
  ├── seller (N:1) → User.products
  ├── cart_items (1:N) → CartItem.product
  └── order_items (1:N) → OrderItem.product

Order
  ├── user (N:1) → User.orders
  └── order_items (1:N) → OrderItem.order
```

---

### 3. **requirements.txt** - Dependencies
**Purpose:** List of all Python packages needed

**Included Packages:**
```
fastapi==0.104.1          # Web Framework
uvicorn[standard]==0.24.0 # ASGI Server
sqlalchemy==2.0.23        # ORM
aiosqlite==0.19.0         # Async SQLite
pydantic==2.5.0           # Data Validation
python-jose==3.3.0        # JWT Handling
passlib[bcrypt]==1.7.4    # Password Hashing
PyJWT==2.8.1             # JWT Encoding/Decoding
python-multipart==0.0.6  # Form Data Handling
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

## 🎨 Frontend Files

### 4. **templates/index.html** - Customer Hub
**Purpose:** Main customer-facing storefront

**Features:**
- Header with navigation and shopping cart
- Product grid with filtering
- Product details and pricing
- Floating shopping cart sidebar
- Login/Register modal
- Order history view
- Responsive design
- Toast notifications

**Key Sections:**
- Header (Logo, Navigation, Cart Icon, User Menu)
- Products Section (Grid display with filters)
- Orders Section (Order history)
- Floating Cart (Side panel)
- Login Modal
- Toast Notifications

**Technologies:** HTML5, CSS3, Vanilla JavaScript

---

### 5. **templates/admin.html** - Seller Portal
**Purpose:** Seller/Admin dashboard for product and order management

**Features:**
- Dashboard with sales statistics
- Product upload and management
- Inventory tracking
- Order management with status updates
- Real-time analytics

**Key Sections:**
- Dashboard Stats (Products, Orders, Revenue)
- Products Tab (Table view of products)
- Upload Tab (New product form)
- Orders Tab (Seller's received orders)
- Edit Product Modal

**Technologies:** HTML5, CSS3, Vanilla JavaScript

---

### 6. **static/app.js** - Frontend Controller
**Purpose:** All client-side logic and API communication

**Main Functions:**

**Utilities:**
- `getCookie(name)` - Get cookie value
- `showToast(message)` - Show notification
- `showSection(name)` - Switch between sections

**Authentication:**
- `showLoginModal()` - Open login dialog
- `handleLogin()` - Process login/register
- `updateAuthUI(user)` - Update user display
- `logout()` - Logout user

**Products:**
- `loadProducts()` - Fetch all products
- `displayProducts(products)` - Render product grid
- `filterProducts()` - Filter by category

**Cart:**
- `toggleCart()` - Open/close cart sidebar
- `loadCart()` - Fetch cart items
- `displayCart(items)` - Render cart
- `addToCart(productId)` - Add product to cart
- `removeFromCart(cartItemId)` - Remove item

**Orders:**
- `checkout()` - Create order from cart
- `loadOrders()` - Fetch user's orders
- `displayOrders(orders)` - Render order history

**API Integration:**
- All API calls via Fetch API
- Automatic cookie handling
- Error handling with toast notifications
- Credentials mode for authentication

---

## 📚 Documentation Files

### 7. **README.md** - Main Documentation
**Purpose:** Complete project overview and getting started guide

**Contains:**
- Architecture explanation
- Quick start guide
- Feature list
- Authentication details
- API endpoints overview
- Database schema
- Development guide
- Customization options
- Testing procedures
- Technology stack
- Production guidelines

**Read this first!** It has all the information needed to understand and run the project.

---

### 8. **DEPLOYMENT.md** - Deployment Guide
**Purpose:** Step-by-step deployment instructions for various environments

**Covers:**
- Development setup
- Staging environment
- Production deployment
  - Architecture overview
  - Prerequisites
  - Gunicorn setup
  - Nginx configuration
  - SSL/TLS with Let's Encrypt
  - Monitoring and logging
  - Backup & recovery
- Docker deployment
  - Dockerfile
  - Docker Compose
- Cloud platforms
  - AWS (EC2 + RDS)
  - Heroku
  - Google Cloud Run
- Performance optimization
- Troubleshooting

**Use this when deploying to production or cloud platforms.**

---

### 9. **API_TESTING.md** - API Testing Guide
**Purpose:** Complete guide for testing all API endpoints

**Includes:**
- Quick start
- curl commands for all endpoints
- Postman collection setup
- Python testing examples
  - Using requests library
  - Using pytest
- Load testing with Locust
- Error response examples
- Performance benchmarks
- Debugging tips

**Use this for manual testing, automated tests, and load testing.**

---

### 10. **PROJECT_STRUCTURE.md** - This File
**Purpose:** Documentation of project structure and file purposes

---

## ⚙️ Configuration Files

### 11. **.env.example** - Environment Template
**Purpose:** Template for environment variables

**Variables:**
```
DATABASE_URL      # Database connection string
SECRET_KEY        # JWT secret key
JWT_ALGORITHM     # Token algorithm
HOST/PORT         # Server configuration
SMS_PROVIDER      # SMS service configuration
EMAIL settings    # Email notifications
Logging config    # Log level and files
Feature flags     # Enable/disable features
```

**Usage:**
```bash
cp .env.example .env
# Edit .env with your values
```

---

## 🚀 Setup Scripts

### 12. **setup.sh** - Linux/macOS Setup
**Purpose:** Automated setup for Unix-like systems

**Does:**
- Check Python installation
- Create virtual environment
- Install dependencies
- Create .env file
- Create necessary directories

**Usage:**
```bash
chmod +x setup.sh
./setup.sh
```

---

### 13. **setup.bat** - Windows Setup
**Purpose:** Automated setup for Windows

**Does:** (Same as setup.sh)

**Usage:**
```bash
setup.bat
```

---

## 📊 Database File

### 14. **ecommerce.db** - SQLite Database
**Purpose:** Local SQLite database (auto-created)

**Auto-created on first run**
**Contains:** All application data (users, products, orders, etc.)
**Backup:** Should be backed up before deployment

**Inspect:**
```bash
sqlite3 ecommerce.db
sqlite> .tables
sqlite> SELECT * FROM users;
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│          Frontend (index.html + app.js)             │
│                                                     │
│  - Product Browsing    - Shopping Cart             │
│  - User Auth           - Checkout                  │
│  - Order Viewing       - Filter/Search             │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ HTTP/REST API
                   │
┌──────────────────▼──────────────────────────────────┐
│         FastAPI Application (main.py)              │
│                                                     │
│  - Route Handlers      - Business Logic            │
│  - Authentication      - Validation                │
│  - Request Processing  - Response Formatting      │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ SQLAlchemy ORM
                   │
┌──────────────────▼──────────────────────────────────┐
│    Database Layer (database.py)                     │
│                                                     │
│  - Models (User, Product, Order, etc.)            │
│  - Async Queries       - Relationships             │
│  - Connection Pool     - Password Hashing          │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ SQLite/PostgreSQL
                   │
┌──────────────────▼──────────────────────────────────┐
│    Database (ecommerce.db or PostgreSQL)           │
│                                                     │
│  - User data      - Product inventory              │
│  - Orders         - Cart items                     │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 File Access Patterns

### Customer Using App
1. Opens `index.html` (loaded by `main.py`)
2. JavaScript (`app.js`) loads products from API
3. Adds items to cart → calls `/api/cart/add`
4. Clicks checkout → calls `/api/checkout`
5. API verifies stock via `database.py`
6. Order created in `ecommerce.db`

### Seller Using Admin
1. Opens `admin.html` (loaded by `main.py`)
2. Uploads products → calls `/api/products`
3. `main.py` validates and creates Product in `database.py`
4. Data stored in `ecommerce.db`
5. Seller views orders → calls `/api/orders`

### API Consumer (Mobile App, etc.)
1. Calls endpoints directly from `main.py`
2. Responses from database via `database.py`
3. No frontend files needed

---

## 📦 Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Clone/download project files
- [ ] Run setup.sh (Linux/macOS) or setup.bat (Windows)
- [ ] Create .env file (copy from .env.example)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Start application: `python main.py`
- [ ] Test in browser: http://localhost:8000
- [ ] Test API: http://localhost:8000/docs

---

## 🔍 Finding Things

| What I need... | Look in... |
|---|---|
| Product listing endpoint | `main.py` - `/api/products` |
| Cart logic | `app.js` - `loadCart()`, `addToCart()` |
| Database schema | `database.py` - Model classes |
| Authentication | `main.py` - Auth routes; `app.js` - handleLogin() |
| Product creation | `main.py` - POST /api/products |
| Order processing | `main.py` - /api/checkout |
| Frontend styling | `index.html`, `admin.html` - <style> tags |
| API documentation | http://localhost:8000/docs (Swagger UI) |

---

## 🛠️ Development Workflow

1. **Make Changes**
   - Edit `main.py` for API changes
   - Edit `app.js` for frontend logic
   - Edit HTML for layout/design

2. **Test Changes**
   - Restart `python main.py`
   - Refresh browser
   - Check console for errors (F12)
   - Test API endpoints (use curl or Postman)

3. **Database Changes**
   - Edit model in `database.py`
   - SQLAlchemy auto-creates/migrates tables
   - Restart application

4. **Deploy**
   - Follow `DEPLOYMENT.md`
   - Change `DATABASE_URL` to production database
   - Update `SECRET_KEY`
   - Use production ASGI server (Gunicorn)

---

**Last Updated:** 2024
**Version:** 1.0.0
**Created for:** ShopHub E-Commerce Platform
