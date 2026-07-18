"""
main.py - The FastAPI Application Brain
FastAPI + Uvicorn application with routing, controllers, authentication, and business logic
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field
import jwt
from fastapi import FastAPI, HTTPException, Depends, Cookie, Response, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from contextlib import asynccontextmanager

# Import database components
from database import (
    db_manager, Base, User, Product, CartItem, Order, OrderItem,
    get_user_by_username, get_user_by_id, get_product_by_id, 
    get_products_by_category, get_all_products, get_cart_items,
    get_user_orders, verify_stock
)

# ============= CONFIGURATION =============

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# ============= PYDANTIC MODELS (API Schemas) =============

class UserCreate(BaseModel):
    username: str
    password: str
    mobile: Optional[str] = None
    role: str = "customer"


class UserResponse(BaseModel):
    id: int
    username: str
    mobile: Optional[str]
    role: str


class ProductCreate(BaseModel):
    name: str
    description: str
    category: str
    price: float
    stock: int
    image_path: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    price: float
    stock: int
    image_path: Optional[str]
    seller_id: int

    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    timestamp: datetime
    user_mobile: str
    status: str
    order_items: List[OrderItemResponse]

    class Config:
        from_attributes = True


# ============= AUTHENTICATION & JWT =============

def create_access_token(user_id: int, username: str) -> str:
    """Create JWT token"""
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": int(user_id), "username": payload.get("username")}
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(session: AsyncSession, token: Optional[str] = Cookie(None)) -> Optional[User]:
    """Dependency to get current authenticated user"""
    if not token:
        return None
    payload = verify_token(token)
    if not payload:
        return None
    user = await get_user_by_id(session, payload["user_id"])
    return user


async def require_auth(current_user: Optional[User] = Depends(get_current_user)) -> User:
    """Require authenticated user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user


# ============= FASTAPI APPLICATION =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    await db_manager.initialize()
    print("✓ Database initialized")
    yield
    # Shutdown
    await db_manager.close()
    print("✓ Database closed")


app = FastAPI(
    title="E-Commerce API",
    description="Multi-vendor e-commerce platform with async database",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# ============= AUTHENTICATION ROUTES =============

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    async with db_manager.get_session() as session:
        # Check if username exists
        existing_user = await get_user_by_username(session, user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create new user
        new_user = User(
            username=user_data.username,
            mobile=user_data.mobile,
            role=user_data.role
        )
        new_user.set_password(user_data.password)
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        return new_user


@app.post("/api/auth/login")
async def login(user_data: UserCreate, response: Response):
    """Login user and return JWT token"""
    async with db_manager.get_session() as session:
        user = await get_user_by_username(session, user_data.username)
        
        if not user or not user.verify_password(user_data.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_access_token(user.id, user.username)
        response.set_cookie(key="token", value=token, httponly=True, max_age=7*24*3600)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }


@app.post("/api/auth/logout")
async def logout(response: Response):
    """Logout user"""
    response.delete_cookie(key="token")
    return {"message": "Logged out successfully"}


# ============= USER ROUTES =============

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(require_auth)):
    """Get current user info"""
    return current_user


# ============= PRODUCT ROUTES =============

@app.get("/api/products", response_model=List[ProductResponse])
async def list_products(category: Optional[str] = None):
    """List all products or filter by category"""
    async with db_manager.get_session() as session:
        if category:
            products = await get_products_by_category(session, category)
        else:
            products = await get_all_products(session)
        return products


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Get product details"""
    async with db_manager.get_session() as session:
        product = await get_product_by_id(session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product


@app.post("/api/products", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_auth)
):
    """Create a new product (seller only)"""
    if current_user.role not in ["seller", "admin"]:
        raise HTTPException(status_code=403, detail="Only sellers can create products")
    
    async with db_manager.get_session() as session:
        new_product = Product(
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            price=product_data.price,
            stock=product_data.stock,
            image_path=product_data.image_path,
            seller_id=current_user.id
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product


# ============= CART ROUTES =============

@app.get("/api/cart", response_model=List[CartItemResponse])
async def get_cart(current_user: User = Depends(require_auth)):
    """Get user's shopping cart"""
    async with db_manager.get_session() as session:
        cart_items = await get_cart_items(session, current_user.id)
        return cart_items


@app.post("/api/cart/add")
async def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(require_auth)
):
    """Add item to cart"""
    async with db_manager.get_session() as session:
        # Verify product exists
        product = await get_product_by_id(session, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if item already in cart
        stmt = select(CartItem).where(
            (CartItem.user_id == current_user.id) & 
            (CartItem.product_id == item.product_id)
        )
        result = await session.execute(stmt)
        existing_item = result.scalar_one_or_none()
        
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            session.add(cart_item)
        
        await session.commit()
        return {"message": "Item added to cart"}


@app.delete("/api/cart/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: int,
    current_user: User = Depends(require_auth)
):
    """Remove item from cart"""
    async with db_manager.get_session() as session:
        cart_item = await session.get(CartItem, cart_item_id)
        
        if not cart_item or cart_item.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        await session.delete(cart_item)
        await session.commit()
        
        return {"message": "Item removed from cart"}


@app.post("/api/cart/clear")
async def clear_cart(current_user: User = Depends(require_auth)):
    """Clear entire shopping cart"""
    async with db_manager.get_session() as session:
        stmt = select(CartItem).where(CartItem.user_id == current_user.id)
        result = await session.execute(stmt)
        items = result.scalars().all()
        
        for item in items:
            await session.delete(item)
        
        await session.commit()
        return {"message": "Cart cleared"}


# ============= CHECKOUT & ORDERS =============

@app.post("/api/checkout", response_model=OrderResponse)
async def checkout(
    current_user: User = Depends(require_auth)
):
    """Checkout - create order from cart items"""
    async with db_manager.get_session() as session:
        # Get cart items
        cart_items = await get_cart_items(session, current_user.id)
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Verify stock for all items
        total_price = 0
        for cart_item in cart_items:
            product = cart_item.product
            
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for {product.name}"
                )
            
            total_price += product.price * cart_item.quantity
        
        # Create order
        order = Order(
            user_id=current_user.id,
            total_price=total_price,
            user_mobile=current_user.mobile or "N/A",
            status="pending"
        )
        session.add(order)
        await session.flush()  # Get order ID
        
        # Create order items and update stock
        for cart_item in cart_items:
            product = cart_item.product
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_at_purchase=product.price
            )
            session.add(order_item)
            
            # Update product stock
            product.stock -= cart_item.quantity
        
        # Clear cart
        for cart_item in cart_items:
            await session.delete(cart_item)
        
        await session.commit()
        await session.refresh(order)
        
        # Send SMS receipt (simulated)
        await send_sms_receipt(current_user.mobile, order)
        
        return order


@app.get("/api/orders", response_model=List[OrderResponse])
async def get_orders(current_user: User = Depends(require_auth)):
    """Get user's orders"""
    async with db_manager.get_session() as session:
        orders = await get_user_orders(session, current_user.id)
        return orders


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(require_auth)
):
    """Get order details"""
    async with db_manager.get_session() as session:
        order = await session.get(Order, order_id)
        
        if not order or order.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return order


@app.put("/api/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    current_user: User = Depends(require_auth)
):
    """Update order status (admin/seller only)"""
    if current_user.role not in ["admin", "seller"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    async with db_manager.get_session() as session:
        order = await session.get(Order, order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if status not in ["pending", "confirmed", "shipped", "delivered"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        order.status = status
        await session.commit()
        
        return {"message": f"Order status updated to {status}"}


# ============= UTILITY FUNCTIONS =============

async def send_sms_receipt(mobile: str, order: Order):
    """
    Simulate sending SMS receipt
    In production, integrate with SMS provider (Twilio, AWS SNS, etc.)
    """
    if mobile and mobile != "N/A":
        message = f"Order #{order.id} confirmed! Total: ₹{order.total_price}. Items will be shipped soon."
        print(f"[SMS] {mobile}: {message}")
        # TODO: Integrate with SMS provider
        return True
    return False


# ============= FRONTEND ROUTES =============

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve customer hub"""
    with open("templates/index.html", "r") as f:
        return f.read()


@app.get("/admin", response_class=HTMLResponse)
async def admin():
    """Serve seller portal"""
    with open("templates/admin.html", "r") as f:
        return f.read()


# ============= HEALTH CHECK =============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": "connected"
    }


# ============= ERROR HANDLERS =============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
