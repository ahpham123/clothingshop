document.addEventListener('DOMContentLoaded', async function() {
    // Generate a simple user ID for demo purposes
    const USER_ID = localStorage.getItem('user_id') || 'user_' + Math.floor(Math.random() * 10000);
    localStorage.setItem('user_id', USER_ID);
    
    // Initialize cart display
    const cartCount = document.getElementById('cart-count');
    updateCartDisplay();
    
    // Handle page-specific content
    const currentPage = window.location.pathname;
    
    if (currentPage === '/' || currentPage === '/index') {
        // Home page - show featured products
        await loadFeaturedProducts();
    } else if (currentPage === '/products') {
        // Products page - show all products with filtering
        await loadAllProducts();
    }
    
    // Add event listener for navigation
    document.querySelector('nav').addEventListener('click', function(e) {
        if (e.target.textContent.includes('Cart')) {
            e.preventDefault();
            showCartModal();
        }
    });
    
    async function loadFeaturedProducts() {
        try {
            const products = await fetchProducts();
            displayProducts(products.slice(0, 4), 'product-grid'); // Display only first 4 products
        } catch (error) {
            console.error('Error loading featured products:', error);
            document.getElementById('product-grid').innerHTML = '<p class="error">Failed to load products. Please try again later.</p>';
        }
    }
    
    async function loadAllProducts() {
        try {
            const products = await fetchProducts();
            
            // Add category filters
            const categories = [...new Set(products.map(product => product.category))];
            createCategoryFilters(categories);
            
            // Display all products
            displayProducts(products, 'all-products-grid');
            
            // Set up filter functionality
            setupFilters(products);
        } catch (error) {
            console.error('Error loading products:', error);
            document.getElementById('all-products-grid').innerHTML = '<p class="error">Failed to load products. Please try again later.</p>';
        }
    }
    
    function createCategoryFilters(categories) {
        const filterContainer = document.getElementById('product-filters');
        if (!filterContainer) return;
        
        // Create "All" filter
        const allFilter = document.createElement('button');
        allFilter.className = 'filter-btn active';
        allFilter.textContent = 'All';
        allFilter.setAttribute('data-category', 'all');
        filterContainer.appendChild(allFilter);
        
        // Create category filters
        categories.forEach(category => {
            const button = document.createElement('button');
            button.className = 'filter-btn';
            button.textContent = category.charAt(0).toUpperCase() + category.slice(1);
            button.setAttribute('data-category', category);
            filterContainer.appendChild(button);
        });
    }
    
    function setupFilters(products) {
        const filterButtons = document.querySelectorAll('.filter-btn');
        if (!filterButtons.length) return;
        
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                const category = this.getAttribute('data-category');
                let filteredProducts;
                
                if (category === 'all') {
                    filteredProducts = products;
                } else {
                    filteredProducts = products.filter(product => product.category === category);
                }
                
                displayProducts(filteredProducts, 'all-products-grid');
            });
        });
    }
    
    function displayProducts(products, containerId) {
        const productGrid = document.getElementById(containerId);
        if (!productGrid) return;
        
        productGrid.innerHTML = '';
        
        if (products.length === 0) {
            productGrid.innerHTML = '<p class="no-products">No products found in this category.</p>';
            return;
        }
        
        products.forEach(product => {
            // Adjust for the new structure - rating is now separate fields
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
                <img src="${product.image}" alt="${product.title}" class="product-image">
                <div class="product-info">
                    <h3 class="product-title">${truncateText(product.title, 40)}</h3>
                    <p class="product-category">${product.category}</p>
                    <p class="product-price">$${product.price.toFixed(2)}</p>
                    <div class="product-rating">
                        <span class="stars">${getStarRating(product.rating_rate || 0)}</span>
                        <span class="count">(${product.rating_count || 0})</span>
                    </div>
                    <button class="add-to-cart" data-id="${product.id}">Add to Cart</button>
                </div>
            `;
            productGrid.appendChild(productCard);
        });
        
        // Add click event listeners to "Add to Cart" buttons
        productGrid.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', async function() {
                const productId = parseInt(this.getAttribute('data-id'));
                await addToCart(productId, this);
            });
        });
    }
    
    async function addToCart(productId, buttonElement) {
        try {
            const response = await fetch('/api/cart/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: USER_ID,
                    product_id: productId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update UI
                buttonElement.textContent = 'Added!';
                setTimeout(() => {
                    buttonElement.textContent = 'Add to Cart';
                }, 1000);
                
                // Update cart count
                updateCartDisplay();
            } else {
                console.error('Error adding to cart:', data.error);
                buttonElement.textContent = 'Failed';
                setTimeout(() => {
                    buttonElement.textContent = 'Add to Cart';
                }, 1000);
            }
        } catch (error) {
            console.error('Failed to add to cart:', error);
            buttonElement.textContent = 'Error';
            setTimeout(() => {
                buttonElement.textContent = 'Add to Cart';
            }, 1000);
        }
    }
    
    async function updateCartDisplay() {
        try {
            const response = await fetch(`/api/cart?user_id=${USER_ID}`);
            const cartItems = await response.json();
            
            const totalItems = cartItems.reduce((total, item) => total + item.quantity, 0);
            cartCount.textContent = totalItems;
        } catch (error) {
            console.error('Error updating cart:', error);
            cartCount.textContent = '?';
        }
    }
    
    function showCartModal() {
        // Implementation for showing cart modal will be added in future updates
        alert('Cart functionality coming soon!');
    }
    
    function truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    function getStarRating(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        let stars = '';
        for (let i = 0; i < fullStars; i++) stars += '★';
        if (halfStar) stars += '½';
        for (let i = 0; i < emptyStars; i++) stars += '☆';
        
        return stars;
    }
});

async function fetchProducts() {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching products:', error);
        throw error;
    }
}

// Cart functionality
class Cart {
    constructor() {
        this.userId = this.getOrCreateUserId();
        this.cartItems = [];
        this.loadCart();
    }

    getOrCreateUserId() {
        let userId = localStorage.getItem('userId');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('userId', userId);
        }
        return userId;
    }

    async loadCart() {
        try {
            const response = await fetch(`/api/cart?user_id=${this.userId}`);
            if (response.ok) {
                this.cartItems = await response.json();
                this.updateCartCount();
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    }

    async addItem(productId) {
        try {
            const response = await fetch('/api/cart/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    product_id: productId
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.cartItems = data.cart;
                this.updateCartCount();
                this.showSuccessMessage('Item added to cart!');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
        }
    }

    async removeItem(productId) {
        try {
            const response = await fetch('/api/cart/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    product_id: productId
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.cartItems = data.cart;
                this.updateCartCount();
                if (window.location.pathname === '/cart') {
                    this.displayCartItems();
                }
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
        }
    }

    updateCartCount() {
        const count = this.cartItems.reduce((total, item) => total + item.quantity, 0);
        document.querySelectorAll('#cart-count').forEach(el => {
            el.textContent = count;
        });
    }

    showSuccessMessage(message) {
        const msg = document.createElement('div');
        msg.className = 'cart-message';
        msg.textContent = message;
        document.body.appendChild(msg);
        setTimeout(() => msg.remove(), 3000);
    }

    async displayCartItems() {
        const cartContainer = document.getElementById('cart-container');
        if (!cartContainer) return;

        if (this.cartItems.length === 0) {
            cartContainer.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
            return;
        }

        let html = `
            <div class="cart-items">
                <div class="cart-header">
                    <div class="header-item">Product</div>
                    <div class="header-item">Price</div>
                    <div class="header-item">Quantity</div>
                    <div class="header-item">Total</div>
                    <div class="header-item">Action</div>
                </div>
        `;

        let total = 0;
        
        this.cartItems.forEach(item => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;
            
            html += `
                <div class="cart-item" data-id="${item.product_id}">
                    <div class="cart-item-product">
                        <img src="${item.image}" alt="${item.title}" class="cart-item-image">
                        <div class="cart-item-title">${item.title}</div>
                    </div>
                    <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                    <div class="cart-item-quantity">${item.quantity}</div>
                    <div class="cart-item-total">$${itemTotal.toFixed(2)}</div>
                    <div class="cart-item-action">
                        <button class="remove-from-cart" data-id="${item.product_id}">Remove</button>
                    </div>
                </div>
            `;
        });

        html += `
            </div>
            <div class="cart-summary">
                <div class="cart-total">
                    <span>Total:</span>
                    <span class="total-amount">$${total.toFixed(2)}</span>
                </div>
                <button class="checkout-btn">Proceed to Checkout</button>
            </div>
        `;

        cartContainer.innerHTML = html;

        // Add event listeners to remove buttons
        document.querySelectorAll('.remove-from-cart').forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = parseInt(e.target.getAttribute('data-id'));
                this.removeItem(productId);
            });
        });
    }
}

// Initialize cart
const cart = new Cart();

// Make cart available globally for debugging
window.cart = cart;

// Product display functions
async function fetchProducts() {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error fetching products:', error);
        return [];
    }
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    card.innerHTML = `
        <img src="${product.image}" alt="${product.title}" class="product-image">
        <div class="product-info">
            <h3 class="product-title">${product.title}</h3>
            <span class="product-category">${product.category}</span>
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <div class="product-rating">
                <span class="stars">${'★'.repeat(Math.round(product.rating_rate))}${'☆'.repeat(5 - Math.round(product.rating_rate))}</span>
                <span class="count">(${product.rating_count})</span>
            </div>
            <button class="add-to-cart" data-id="${product.id}">Add to Cart</button>
        </div>
    `;
    
    return card;
}

// Load products on home page
if (document.getElementById('product-grid')) {
    fetchProducts().then(products => {
        const featuredProducts = products.slice(0, 4); // Show first 4 as featured
        const grid = document.getElementById('product-grid');
        
        featuredProducts.forEach(product => {
            grid.appendChild(createProductCard(product));
        });
        
        // Add event listeners to add-to-cart buttons
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = parseInt(e.target.getAttribute('data-id'));
                cart.addItem(productId);
            });
        });
    });
}

// Load all products on products page
if (document.getElementById('all-products-grid')) {
    fetchProducts().then(products => {
        const grid = document.getElementById('all-products-grid');
        grid.innerHTML = ''; // Remove loading message
        
        products.forEach(product => {
            grid.appendChild(createProductCard(product));
        });
        
        // Add event listeners to add-to-cart buttons
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = parseInt(e.target.getAttribute('data-id'));
                cart.addItem(productId);
            });
        });
    });
}


// Handle cart link click
document.querySelectorAll('#cart-link, nav ul li a[href="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = '/cart';
    });
});

// Display cart items if on cart page
if (window.location.pathname === '/cart') {
    cart.displayCartItems();
}