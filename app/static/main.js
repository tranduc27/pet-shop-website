// API Base URL
const API_URL = ''; // Same origin

// Current State
let currentUser = null;
let cartCount = 0;

// Initialize app on load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    
    if (document.getElementById('home')) {
        fetchProducts('/products/latest?limit=10');
    }
    
    // Auth Form Listeners
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        document.getElementById('register-form').addEventListener('submit', handleRegister);
    }
});

// --- UI / Modal Utilities ---
function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent scrolling
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
    document.body.style.overflow = 'auto';
    // Clear forms and errors
    clearForm(modalId);
}

function switchModal(fromId, toId) {
    closeModal(fromId);
    setTimeout(() => openModal(toId), 300); // Wait for transition
}

function clearForm(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const form = modal.querySelector('form');
        if (form) form.reset();
        const errorMsg = modal.querySelector('.error-msg');
        if (errorMsg) errorMsg.classList.add('hidden');
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-circle-exclamation';
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });
    
    // Remove after 3s
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function showError(formId, message) {
    const errorEl = document.getElementById(formId);
    errorEl.textContent = message;
    errorEl.classList.remove('hidden');
}

// --- Auth Handling ---
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');
    
    const authButtons = document.getElementById('auth-buttons');
    const userInfo = document.getElementById('user-info');
    const usernameDisplay = document.getElementById('username-display');
    
    if (token && username) {
        // Logged in
        authButtons.classList.add('hidden');
        userInfo.classList.remove('hidden');
        usernameDisplay.textContent = `Xin chào, ${username}`;
        currentUser = { username, token };
        loadCartCount();
    } else {
        // Not logged in
        authButtons.classList.remove('hidden');
        userInfo.classList.add('hidden');
        currentUser = null;
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
    btn.disabled = true;

    const formData = new FormData();
    formData.append('username', document.getElementById('login-username').value);
    formData.append('password', document.getElementById('login-password').value);

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            body: formData // OAuth2PasswordRequestForm expects FormData
        });

        const data = await res.json();
        
        if (res.ok) {
            localStorage.setItem('access_token', data.access_token);
            // Decode token manually or just save username from input
            localStorage.setItem('username', document.getElementById('login-username').value);
            
            closeModal('login-modal');
            showToast('Đăng nhập thành công!');
            checkAuthStatus();
        } else {
            showError('login-error', data.detail || 'Sai tài khoản hoặc mật khẩu');
        }
    } catch (err) {
        showError('login-error', 'Lỗi kết nối máy chủ');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm').value;

    if (password !== confirm) {
        showError('reg-error', 'Mật khẩu xác nhận không khớp');
        return;
    }

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role: 'Customer' })
        });

        const data = await res.json();

        if (res.ok) {
            showToast('Đăng ký thành công! Vui lòng đăng nhập.');
            switchModal('register-modal', 'login-modal');
            // Auto-fill username
            document.getElementById('login-username').value = username;
        } else {
            showError('reg-error', data.detail || 'Lỗi đăng ký');
        }
    } catch (err) {
        showError('reg-error', 'Lỗi kết nối máy chủ');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    checkAuthStatus();
    showToast('Đã đăng xuất');
}

// --- Product APIs ---
async function fetchProducts(endpoint = '/products/') {
    const grid = document.getElementById('product-grid');
    if (!grid) return;
    
    try {
        const res = await fetch(`${API_URL}${endpoint}`);
        const data = await res.json();
        
        if (res.ok) {
            renderProducts(data);
        } else {
            grid.innerHTML = '<p class="error-msg">Không thể tải danh sách sản phẩm.</p>';
        }
    } catch (err) {
        grid.innerHTML = '<p class="error-msg">Lỗi kết nối máy chủ. Vui lòng thử lại sau.</p>';
    }
}

function renderProducts(products) {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';
    
    if (products.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">Chưa có sản phẩm nào trong cửa hàng.</p>';
        return;
    }
    
    products.forEach(p => {
        // Fallback images if not exists
        let imageUrl = p.image_url || '';
        // If image URL is missing or local, we can put a placeholder
        if (!imageUrl || imageUrl.trim() === '') {
            imageUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(p.name)}&background=random&size=256`;
        }
        
        // Format price to VND
        const formatter = new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND',
        });
        const formattedPrice = formatter.format(p.price);
        
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            ${p.stock > 0 ? `<div class="stock-badge">Còn ${p.stock}</div>` : `<div class="stock-badge" style="color:red">Hết hàng</div>`}
            <img src="${imageUrl}" alt="${p.name}" class="product-image" onerror="this.src='https://ui-avatars.com/api/?name=Pet&background=f77f00&color=fff&size=256'">
            <div class="product-info">
                <h3 class="product-title">${p.name}</h3>
                <p class="product-desc">${p.description || 'Sản phẩm tuyệt vời cho thú cưng của bạn.'}</p>
                <div class="product-footer">
                    <span class="product-price">${formattedPrice}</span>
                    <button class="btn-add-cart" onclick="addToCart(${p.id}, '${p.name}')" ${p.stock <= 0 ? 'disabled' : ''} title="Thêm vào giỏ">
                        <i class="fa-solid fa-cart-plus"></i>
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// --- Cart APIs ---
async function loadCartCount() {
    if (!currentUser) return;
    try {
        const res = await fetch(`${API_URL}/cart/`, {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        if (res.ok) {
            const data = await res.json();
            const count = data.reduce((sum, item) => sum + item.quantity, 0);
            document.querySelector('.cart-count').textContent = count;
        }
    } catch(err) {
        console.error('Error loading cart count:', err);
    }
}

async function addToCart(productId, productName) {
    // Check if logged in
    if (!currentUser) {
        showToast('Vui lòng đăng nhập để thêm vào giỏ hàng', 'error');
        openModal('login-modal');
        return;
    }
    
    try {
        const res = await fetch(`${API_URL}/cart/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token}`
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });
        
        if (res.ok) {
            loadCartCount();
            
            // Animation for cart icon
            const cartIcon = document.querySelector('.cart-icon');
            cartIcon.style.transform = 'scale(1.2)';
            setTimeout(() => {
                cartIcon.style.transform = 'scale(1)';
            }, 200);
            
            showToast(`Đã thêm ${productName} vào giỏ!`);
            
            // If cart modal is open, reload it
            if (!document.getElementById('cart-modal').classList.contains('hidden')) {
                loadCart();
            }
        } else {
            showToast('Thêm vào giỏ thất bại', 'error');
        }
    } catch (err) {
        showToast('Lỗi kết nối máy chủ', 'error');
    }
}

async function loadCart() {
    const cartItemsContainer = document.getElementById('cart-items');
    cartItemsContainer.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-spinner fa-spin"></i> Đang tải...</div>';
    
    try {
        const res = await fetch(`${API_URL}/cart/`, {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            renderCart(data);
        } else {
            cartItemsContainer.innerHTML = '<p class="error-msg">Không thể tải giỏ hàng.</p>';
        }
    } catch (err) {
        cartItemsContainer.innerHTML = '<p class="error-msg">Lỗi kết nối máy chủ.</p>';
    }
}

function renderCart(items) {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total-price');
    container.innerHTML = '';
    
    if (items.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin-top: 2rem;">Giỏ hàng của bạn đang trống.</p>';
        totalEl.textContent = '0 ₫';
        // Update badge
        document.querySelector('.cart-count').textContent = '0';
        return;
    }
    
    let total = 0;
    let count = 0;
    const formatter = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' });
    
    items.forEach(item => {
        total += item.product.price * item.quantity;
        count += item.quantity;
        
        let imageUrl = item.product.image_url || '';
        if (!imageUrl || imageUrl.trim() === '') {
            imageUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(item.product.name)}&background=random&size=256`;
        }
        
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <img src="${imageUrl}" alt="${item.product.name}" class="cart-item-img">
            <div class="cart-item-info">
                <div>
                    <h4 class="cart-item-title">${item.product.name}</h4>
                    <div class="cart-item-price">${formatter.format(item.product.price)}</div>
                </div>
                <div class="cart-item-controls">
                    <div class="cart-quantity">
                        <span>SL: ${item.quantity}</span>
                    </div>
                    <button class="btn-remove-item" onclick="removeFromCart(${item.id})">
                        <i class="fa-solid fa-trash"></i> Xóa
                    </button>
                </div>
            </div>
        `;
        container.appendChild(div);
    });
    
    totalEl.textContent = formatter.format(total);
    // Update badge synchronously
    document.querySelector('.cart-count').textContent = count;
}

async function removeFromCart(cartId) {
    try {
        const res = await fetch(`${API_URL}/cart/${cartId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        
        if (res.ok) {
            showToast('Đã xóa sản phẩm khỏi giỏ');
            loadCart(); // Reload cart lists
        } else {
            showToast('Xóa thất bại', 'error');
        }
    } catch(err) {
        showToast('Lỗi kết nối', 'error');
    }
}

function toggleCart() {
    if (!currentUser) {
        openModal('login-modal');
    } else {
        openModal('cart-modal');
        loadCart();
    }
}

// --- Checkout API ---
async function handleCheckout() {
    if (!currentUser) {
        showToast('Vui lòng đăng nhập để thanh toán', 'error');
        openModal('login-modal');
        return;
    }
    
    try {
        const btn = document.querySelector('.cart-footer .btn-primary');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xử lý...';
        btn.disabled = true;

        const res = await fetch(`${API_URL}/orders/checkout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        
        if (res.ok) {
            showToast('Thanh toán thành công!');
            closeModal('cart-modal');
            loadCartCount();
            
            // Tải lại các sản phẩm dựa theo trang hiện tại (tùy trang Chủ / Shop)
            if (window.location.pathname.includes('/shop') && typeof loadShopProducts === 'function') {
                loadShopProducts();
            } else if (document.getElementById('home')) {
                fetchProducts('/products/latest?limit=10');
            }
        } else {
            const data = await res.json();
            showToast(data.detail || 'Thanh toán thất bại', 'error');
        }
        
        // Restore button state if not closed
        if (btn) {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (err) {
        showToast('Lỗi kết nối máy chủ', 'error');
    }
}

// --- Slider Utility ---
function slideProducts(direction) {
    const container = document.getElementById('product-grid');
    if (!container) return;
    const scrollAmount = 300; // khoảng cách mỗi lần cuộn
    if (direction === 'left') {
        container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    } else {
        container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
}
