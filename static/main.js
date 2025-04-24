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