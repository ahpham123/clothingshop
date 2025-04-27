document.addEventListener('DOMContentLoaded', async function() {
    // Function to generate a proper UUID
    const generateUUID = () => {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0, 
                v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    };

    // Check for existing user ID
    let USER_ID = localStorage.getItem('user_id');

    // If user ID doesn't exist or is in the old format (starts with "user_"), generate a new UUID
    if (!USER_ID || USER_ID.startsWith('user_')) {
        USER_ID = generateUUID();
        localStorage.setItem('user_id', USER_ID);
    }
    
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
    } else if (currentPage === '/cart') {
        // Cart page - load cart items
        await loadCartPage();
    }
    
    // Add event listener for navigation
    document.querySelector('nav').addEventListener('click', function(e) {
        if (e.target.textContent.includes('Cart')) {
            e.preventDefault();
            window.location.href = '/cart';
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
    
    async function loadCartPage() {
        try {
            const cartContainer = document.getElementById('cart-container');
            if (!cartContainer) return;
            
            const cartItems = await fetchCartItems();
            
            if (cartItems.length === 0) {
                cartContainer.innerHTML = `
                    <div class="empty-cart">
                        <p>Your cart is empty.</p>
                        <a href="/products" class="add-to-cart" style="display: inline-block; margin-top: 20px;">Shop Now</a>
                    </div>
                `;
                return;
            }
            
            // Calculate total
            const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            
            // Create cart HTML
            cartContainer.innerHTML = `
                <div class="cart-items">
                    <div class="cart-header">
                        <div class="header-item">Product</div>
                        <div class="header-item">Price</div>
                        <div class="header-item">Quantity</div>
                        <div class="header-item">Total</div>
                        <div class="header-item">Action</div>
                    </div>
                    <div id="cart-items-list">
                        ${cartItems.map(item => `
                            <div class="cart-item">
                                <div class="cart-item-product">
                                    <img src="${item.image}" alt="${item.title}" class="cart-item-image">
                                    <div class="cart-item-title">${item.title}</div>
                                </div>
                                <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                                <div class="cart-item-quantity">${item.quantity}</div>
                                <div class="cart-item-total">$${(item.price * item.quantity).toFixed(2)}</div>
                                <div class="cart-item-action">
                                    <button class="remove-from-cart" data-id="${item.product_id}">Remove</button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="cart-summary">
                    <div class="cart-total">
                        Total: <span class="total-amount">$${total.toFixed(2)}</span>
                    </div>
                    <button class="checkout-btn">Proceed to Checkout</button>
                </div>
            `;
            
            // Add event listeners to remove buttons
            document.querySelectorAll('.remove-from-cart').forEach(button => {
                button.addEventListener('click', async function() {
                    const productId = parseInt(this.getAttribute('data-id'));
                    await removeFromCart(productId);
                });
            });
            
            // Add event listener to checkout button
            document.querySelector('.checkout-btn').addEventListener('click', async function() {
                try {
                    // Get cart items
                    const cartItems = await fetchCartItems();
                    
                    if (cartItems.length === 0) {
                        alert('Your cart is empty.');
                        return;
                    }
                    
                    // Disable the button during processing
                    this.disabled = true;
                    this.textContent = 'Processing...';
                    
                    // Send checkout request to backend
                    const response = await fetch('/api/checkout', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            user_id: USER_ID,
                            items: cartItems
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        // If server generated a new UUID, update our local storage
                        if (data.new_user_id) {
                            USER_ID = data.new_user_id;
                            localStorage.setItem('user_id', USER_ID);
                            console.log('Updated to new UUID:', USER_ID);
                        }
                        
                        // Show success message
                        alert('Order processed successfully!');
                        
                        // Update cart display
                        updateCartDisplay();
                        
                        // Redirect to confirmation page or show confirmation message
                        // For now, just reload the cart page
                        window.location.reload();
                    } else {
                        console.error('Checkout error:', data.error);
                        alert(`Checkout failed: ${data.error}`);
                        
                        // Re-enable the button
                        this.disabled = false;
                        this.textContent = 'Proceed to Checkout';
                    }
                } catch (error) {
                    console.error('Failed to process checkout:', error);
                    alert('Failed to process checkout. Please try again.');
                    
                    // Re-enable the button
                    this.disabled = false;
                    this.textContent = 'Proceed to Checkout';
                }
            });
            
        } catch (error) {
            console.error('Error loading cart:', error);
            document.getElementById('cart-container').innerHTML = '<p class="error">Failed to load cart. Please try again later.</p>';
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
                        <span class="stars">${getStarRating(product.rating?.rate || 0)}</span>
                        <span class="count">(${product.rating?.count || 0})</span>
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
                // Show success message
                showCartMessage('Product added to cart!');
                
                // Update button
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
    
    async function removeFromCart(productId) {
        try {
            const response = await fetch('/api/cart/remove', {
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
                // Show success message
                showCartMessage('Product removed from cart!');
                
                // Update cart display
                updateCartDisplay();
                
                // Reload cart page
                await loadCartPage();
            } else {
                console.error('Error removing from cart:', data.error);
            }
        } catch (error) {
            console.error('Failed to remove from cart:', error);
        }
    }
    
    async function updateCartDisplay() {
        try {
            const cartItems = await fetchCartItems();
            
            const totalItems = cartItems.reduce((total, item) => total + item.quantity, 0);
            cartCount.textContent = totalItems;
        } catch (error) {
            console.error('Error updating cart:', error);
            cartCount.textContent = '?';
        }
    }
    
    async function fetchCartItems() {
        const response = await fetch(`/api/cart?user_id=${USER_ID}`);
        return await response.json();
    }
    
    function showCartMessage(message) {
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = 'cart-message';
        messageEl.textContent = message;
        
        // Add to DOM
        document.body.appendChild(messageEl);
        
        // Remove after animation completes
        setTimeout(() => {
            messageEl.remove();
        }, 3000);
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