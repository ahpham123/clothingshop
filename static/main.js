document.addEventListener('DOMContentLoaded', function() {
    // Sample product data
    const products = [
        {
            id: 1,
            name: "Wireless Headphones",
            price: 99.99,
            image: "https://via.placeholder.com/300x200?text=Headphones"
        },
        {
            id: 2,
            name: "Smart Watch",
            price: 199.99,
            image: "https://via.placeholder.com/300x200?text=Smart+Watch"
        },
        {
            id: 3,
            name: "Bluetooth Speaker",
            price: 79.99,
            image: "https://via.placeholder.com/300x200?text=Speaker"
        },
        {
            id: 4,
            name: "Laptop Backpack",
            price: 49.99,
            image: "https://via.placeholder.com/300x200?text=Backpack"
        }
    ];

    const productGrid = document.getElementById('product-grid');
    const cartCount = document.getElementById('cart-count');
    let cart = JSON.parse(localStorage.getItem('cart')) || [];

    // Display products
    function displayProducts() {
        productGrid.innerHTML = '';
        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
                <img src="${product.image}" alt="${product.name}" class="product-image">
                <div class="product-info">
                    <h3 class="product-title">${product.name}</h3>
                    <p class="product-price">$${product.price.toFixed(2)}</p>
                    <button class="add-to-cart" data-id="${product.id}">Add to Cart</button>
                </div>
            `;
            productGrid.appendChild(productCard);
        });

        updateCartCount();
    }

    // Update cart count
    function updateCartCount() {
        cartCount.textContent = cart.reduce((total, item) => total + item.quantity, 0);
    }

    // Add to cart
    productGrid.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-cart')) {
            const productId = parseInt(e.target.getAttribute('data-id'));
            const product = products.find(p => p.id === productId);
            
            const existingItem = cart.find(item => item.id === productId);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    quantity: 1
                });
            }
            
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartCount();
            
            // Show feedback
            e.target.textContent = 'Added!';
            setTimeout(() => {
                e.target.textContent = 'Add to Cart';
            }, 1000);
        }
    });

    displayProducts();
});

//replace the hardcoded products with once backend is done:
// async function fetchProducts() {
//     const response = await fetch('/api/products');
//     return await response.json();
// }

//update displayProducts function to use the fetched data