/**
 * app.js - Frontend Controller
 * Handles UI interactions, API calls, authentication, and business logic
 */

// ============= UTILITY FUNCTIONS =============

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionName).classList.add('active');
    
    // Load data for section
    if (sectionName === 'products') {
        loadProducts();
    } else if (sectionName === 'orders') {
        loadOrders();
    }
}

// ============= AUTHENTICATION =============

function showLoginModal() {
    document.getElementById('loginModal').classList.add('open');
}

function closeLoginModal() {
    document.getElementById('loginModal').classList.remove('open');
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    document.getElementById('isRegister').checked = false;
    document.getElementById('mobileField').style.display = 'none';
}

function toggleMobileField() {
    const isRegister = document.getElementById('isRegister').checked;
    document.getElementById('mobileField').style.display = isRegister ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    if (document.getElementById('isRegister')) {
        document.getElementById('isRegister').addEventListener('change', toggleMobileField);
    }
    
    // Check if user is already logged in
    const currentUser = localStorage.getItem('currentUser');
    if (currentUser) {
        updateAuthUI(JSON.parse(currentUser));
        loadProducts();
    } else {
        loadProducts();
    }
});

async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const isRegister = document.getElementById('isRegister').checked;
    const mobile = document.getElementById('mobile').value;

    if (!username || !password) {
        showToast('Please fill in all fields');
        return;
    }

    try {
        if (isRegister) {
            // Register first
            const registerResponse = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username,
                    password,
                    mobile: mobile || null,
                    role: 'customer'
                })
            });

            if (!registerResponse.ok) {
                const error = await registerResponse.json();
                showToast('Registration failed: ' + error.detail);
                return;
            }

            showToast('Registration successful! Logging in...');
        }

        // Login
        const loginResponse = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        if (loginResponse.ok) {
            const data = await loginResponse.json();
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            updateAuthUI(data.user);
            closeLoginModal();
            showToast('Welcome, ' + data.user.username + '!');
            loadCart();
        } else {
            const error = await loginResponse.json();
            showToast('Login failed: ' + error.detail);
        }
    } catch (error) {
        showToast('Error: ' + error.message);
    }
}

async function handleSellerLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showToast('Please fill in all fields');
        return;
    }

    try {
        const loginResponse = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        if (loginResponse.ok) {
            const data = await loginResponse.json();
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            document.getElementById('loginModal').classList.remove('open');
            showToast('Welcome, ' + data.user.username + '!');
            window.location.href = '/admin';
        } else {
            const error = await loginResponse.json();
            showToast('Login failed: ' + error.detail);
        }
    } catch (error) {
        showToast('Error: ' + error.message);
    }
}

function updateAuthUI(user) {
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const userDisplay = document.getElementById('userDisplay');

    if (user) {
        userDisplay.textContent = `👤 ${user.username}`;
        loginBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
    } else {
        userDisplay.textContent = '👤 Guest';
        loginBtn.style.display = 'block';
        logoutBtn.style.display = 'none';
    }
}

async function logout() {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        localStorage.removeItem('currentUser');
        localStorage.removeItem('cart');
        updateAuthUI(null);
        document.getElementById('cartCount').textContent = '0';
        document.getElementById('floatingCart').classList.remove('open');
        showToast('Logged out successfully');
        loadProducts();
    } catch (error) {
        showToast('Error logging out: ' + error.message);
    }
}

// ============= PRODUCTS =============

let allProducts = [];

async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        if (response.ok) {
            allProducts = await response.json();
            displayProducts(allProducts);
        } else {
            showToast('Error loading products');
        }
    } catch (error) {
        showToast('Error: ' + error.message);
    }
}

function displayProducts(products) {
    const grid = document.getElementById('productsGrid');
    
    if (!products || products.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #999;">No products available</div>';
        return;
    }

    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <div class="product-image">
                ${product.image_path ? `<img src="${product.image_path}" style="width: 100%; height: 100%; object-fit: cover;">` : product.name.substring(0, 2).toUpperCase()}
            </div>
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-category">${product.category}</div>
                <div class="product-price">₹${product.price.toFixed(2)}</div>
                <div class="product-stock ${product.stock < 5 ? 'low' : ''}">
                    ${product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                </div>
                <div class="product-actions">
                    <input type="number" class="quantity-input" min="1" value="1" data-product-id="${product.id}">
                    <button class="btn-add-cart" onclick="addToCart(${product.id})" ${product.stock === 0 ? 'disabled' : ''}>
                        Add to Cart
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function filterProducts() {
    const category = document.getElementById('categoryFilter').value;
    const filtered = category ? allProducts.filter(p => p.category === category) : allProducts;
    displayProducts(filtered);
}

// ============= SHOPPING CART =============

let cart = JSON.parse(localStorage.getItem('cart') || '[]');

function toggleCart() {
    document.getElementById('floatingCart').classList.toggle('open');
    loadCart();
}

async function loadCart() {
    const currentUser = localStorage.getItem('currentUser');
    
    if (!currentUser) {
        displayCart(cart);
        return;
    }

    try {
        const response = await fetch('/api/cart', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const cartItems = await response.json();
            displayCart(cartItems);
        } else {
            displayCart(cart);
        }
    } catch (error) {
        displayCart(cart);
    }
}

function displayCart(cartItems) {
    const cartList = document.getElementById('cartItemsList');
    const cartTotal = document.getElementById('cartTotal');
    const cartCount = document.getElementById('cartCount');
    
    if (!cartItems || cartItems.length === 0) {
        cartList.innerHTML = '<div style="padding: 2rem; text-align: center; color: #999;">Your cart is empty</div>';
        cartTotal.textContent = '₹0';
        cartCount.textContent = '0';
        return;
    }

    let total = 0;
    let count = 0;

    cartList.innerHTML = cartItems.map(item => {
        const itemTotal = item.product ? (item.product.price * item.quantity) : (item.price * item.quantity);
        total += itemTotal;
        count += item.quantity;

        return `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.product?.name || item.name}</div>
                    <div class="cart-item-qty">Qty: ${item.quantity}</div>
                    <div class="cart-item-price">₹${itemTotal.toFixed(2)}</div>
                </div>
                <button class="cart-item-remove" onclick="removeFromCart(${item.id})">×</button>
            </div>
        `;
    }).join('');

    cartTotal.textContent = '₹' + total.toFixed(2);
    cartCount.textContent = count;
}

async function addToCart(productId) {
    const quantityInput = document.querySelector(`[data-product-id="${productId}"]`);
    const quantity = parseInt(quantityInput.value);
    const currentUser = localStorage.getItem('currentUser');

    if (!currentUser) {
        // Local cart for non-authenticated users
        const product = allProducts.find(p => p.id === productId);
        const existingItem = cart.find(item => item.id === productId);

        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            cart.push({
                id: productId,
                name: product.name,
                price: product.price,
                quantity: quantity
            });
        }

        localStorage.setItem('cart', JSON.stringify(cart));
        displayCart(cart);
        showToast('Added to cart!');
        return;
    }

    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });

        if (response.ok) {
            showToast('Added to cart!');
            await loadCart();
        } else {
            const error = await response.json();
            showToast('Error: ' + error.detail);
        }
    } catch (error) {
        showToast('Error: ' + error.message);
    }
}

async function removeFromCart(cartItemId) {
    const currentUser = localStorage.getItem('currentUser');

    if (!currentUser) {
        cart = cart.filter(item => item.id !== cartItemId);
        localStorage.setItem('cart', JSON.stringify(cart));
        displayCart(cart);
        return;
    }

    try {
        const response = await fetch(`/api/cart/${cartItemId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            await loadCart();
        } else {
            showToast('Error removing item');
        }
    } catch (error) {
        showToast('Error: ' + error.message);
    }
}

// ============= CHECKOUT =============

async function checkout() {
    const currentUser = localStorage.getItem('currentUser');

    if (!currentUser) {
        showToast('Please login to checkout');
        showLoginModal();
        return;
    }

    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({})
        });

        if (response.ok) {
            const order = await response.json();
            document.getElementById('floatingCart').classList.remove('open');
            localStorage.removeItem('cart');
            cart = [];
            showToast('✅ Order placed successfully! Order ID: ' + order.id);
            await loadCart();
            await loadOrders();
            showSection('orders');
        } else {
            const error = await response.json();
            showToast('Checkout failed: ' + error.detail);
        }
    } catch (error) {
        showToast('Error: ' + error.message);
    }
}

// ============= ORDERS =============

async function loadOrders() {
    const currentUser = localStorage.getItem('currentUser');

    if (!currentUser) {
        document.getElementById('ordersList').innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #999;">
                <p>Please login to view your orders</p>
                <button onclick="showLoginModal()" style="margin-top: 1rem; background: #667eea; color: white; padding: 0.7rem 1.5rem; border-radius: 4px;">Login Now</button>
            </div>
        `;
        return;
    }

    try {
        const response = await fetch('/api/orders', {
            credentials: 'include'
        });

        if (response.ok) {
            const orders = await response.json();
            displayOrders(orders);
        } else {
            showToast('Error loading orders');
        }
    } catch (error) {
        showToast('Error: ' + error.message);
    }
}

function displayOrders(orders) {
    const ordersList = document.getElementById('ordersList');

    if (!orders || orders.length === 0) {
        ordersList.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #999;">
                <p>No orders yet. Start shopping!</p>
            </div>
        `;
        return;
    }

    ordersList.innerHTML = orders.map(order => {
        const statusClass = `status-${order.status}`;
        const orderDate = new Date(order.timestamp).toLocaleDateString();

        return `
            <div class="order-card">
                <div class="order-header">
                    <span class="order-id">Order #${order.id}</span>
                    <span class="order-status ${statusClass}">${order.status.charAt(0).toUpperCase() + order.status.slice(1)}</span>
                </div>
                <div style="color: #999; font-size: 0.9rem; margin-bottom: 1rem;">
                    ${orderDate}
                </div>
                <div class="order-items">
                    ${order.order_items.map(item => `
                        <div class="order-item">
                            <span>Product ID #${item.product_id} × ${item.quantity}</span>
                            <span>₹${(item.price_at_purchase * item.quantity).toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="order-total">
                    <span>Total:</span>
                    <span>₹${order.total_price.toFixed(2)}</span>
                </div>
            </div>
        `;
    }).join('');
}

// ============= INITIALIZATION =============

// Load products on page load
document.addEventListener('DOMContentLoaded', function() {
    const currentUser = localStorage.getItem('currentUser');
    if (currentUser) {
        updateAuthUI(JSON.parse(currentUser));
    }
});
