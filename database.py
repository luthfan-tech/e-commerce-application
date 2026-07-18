"""
database.py - The Async Data Layer
Uses SQLAlchemy 2.0 with AIOSQLITE for async database operations
"""

import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, DateTime, Boolean, ForeignKey,
    select, func, and_
)
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from passlib.context import CryptContext

# Database URL - SQLite with async support
DATABASE_URL = "sqlite+aiosqlite:///./ecommerce.db"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Base for models
Base = declarative_base()

# ============= DATABASE MODELS =============

class User(Base):
    """User table - stores customer and seller data"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    mobile: Mapped[str] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="customer")  # customer/seller/admin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products: Mapped[List["Product"]] = relationship(back_populates="seller")
    cart_items: Mapped[List["CartItem"]] = relationship(back_populates="user")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)


class Product(Base):
    """Product table - inventory management"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(50), index=True)
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    image_path: Mapped[str] = mapped_column(String(255), nullable=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seller: Mapped["User"] = relationship(back_populates="products")
    cart_items: Mapped[List["CartItem"]] = relationship(back_populates="product")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")


class CartItem(Base):
    """CartItem table - shopping cart management"""
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship(back_populates="cart_items")


class Order(Base):
    """Order table - order management"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    user_mobile: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending/confirmed/shipped/delivered
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """OrderItem table - items in an order"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price_at_purchase: Mapped[float] = mapped_column(Float)

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="order_items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


# ============= DATABASE ENGINE & SESSION =============

class AsyncDatabaseManager:
    """Manager for async database operations"""

    def __init__(self):
        self.engine = None
        self.async_session = None

    async def initialize(self):
        """Initialize the async database engine and create tables"""
        self.engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            future=True,
            pool_pre_ping=True,
        )
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        """Close the database connection"""
        if self.engine:
            await self.engine.dispose()

    def get_session(self) -> AsyncSession:
        """Get a new async session"""
        return self.async_session()


# Global database manager
db_manager = AsyncDatabaseManager()


# ============= DATABASE QUERIES =============

async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    """Fetch user by username"""
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Fetch user by ID"""
    return await session.get(User, user_id)


async def get_product_by_id(session: AsyncSession, product_id: int) -> Optional[Product]:
    """Fetch product by ID"""
    return await session.get(Product, product_id)


async def get_products_by_category(session: AsyncSession, category: str) -> List[Product]:
    """Fetch products by category"""
    stmt = select(Product).where(Product.category == category)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_all_products(session: AsyncSession) -> List[Product]:
    """Fetch all products"""
    stmt = select(Product)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_cart_items(session: AsyncSession, user_id: int) -> List[CartItem]:
    """Fetch cart items for a user"""
    stmt = select(CartItem).where(CartItem.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_user_orders(session: AsyncSession, user_id: int) -> List[Order]:
    """Fetch orders for a user"""
    stmt = select(Order).where(Order.user_id == user_id).order_by(Order.timestamp.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def verify_stock(session: AsyncSession, product_id: int, quantity: int) -> bool:
    """Verify if product has enough stock"""
    product = await get_product_by_id(session, product_id)
    return product is not None and product.stock >= quantity
