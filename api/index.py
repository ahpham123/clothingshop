from flask import Flask, redirect, url_for, render_template, jsonify, request
import json
import os

# Our Flask app object
app = Flask(__name__, template_folder='../templates',
            static_folder='../static')

# Sample product data (in a real app, this would come from a database)
PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 99.99,
        "description": "High-quality wireless headphones with noise cancellation",
        "image": "/static/images/headphones.jpg",
        "category": "electronics"
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 199.99,
        "description": "Feature-packed smartwatch with health monitoring",
        "image": "/static/images/smartwatch.jpg",
        "category": "electronics"
    },
    {
        "id": 3,
        "name": "Bluetooth Speaker",
        "price": 79.99,
        "description": "Portable speaker with 20-hour battery life",
        "image": "/static/images/speaker.jpg",
        "category": "electronics"
    },
    {
        "id": 4,
        "name": "Laptop Backpack",
        "price": 49.99,
        "description": "Durable backpack with USB charging port",
        "image": "/static/images/backpack.jpg",
        "category": "accessories"
    }
]

# In-memory "database" for cart (in production, use a real database)
CARTS = {}

@app.route('/')
@app.route('/index')
def index():
    """Our default routes of '/' and '/index'"""
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    """API endpoint to get all products"""
    return jsonify(PRODUCTS)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """API endpoint to get a single product by ID"""
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/cart', methods=['GET', 'POST'])
def handle_cart():
    """API endpoint for cart operations"""
    if request.method == 'GET':
        # Get user's cart (in a real app, you'd have user authentication)
        user_id = request.args.get('user_id', 'default')
        cart = CARTS.get(user_id, [])
        return jsonify(cart)
    
    elif request.method == 'POST':
        # Add item to cart
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400
        
        product = next((p for p in PRODUCTS if p['id'] == product_id), None)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Initialize cart if it doesn't exist
        if user_id not in CARTS:
            CARTS[user_id] = []
        
        # Check if product already in cart
        cart_item = next((item for item in CARTS[user_id] if item['product_id'] == product_id), None)
        
        if cart_item:
            cart_item['quantity'] += quantity
        else:
            CARTS[user_id].append({
                "product_id": product_id,
                "name": product['name'],
                "price": product['price'],
                "image": product['image'],
                "quantity": quantity
            })
        
        return jsonify(CARTS[user_id])

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    """API endpoint to remove item from cart"""
    data = request.get_json()
    user_id = data.get('user_id', 'default')
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    
    if user_id in CARTS:
        CARTS[user_id] = [item for item in CARTS[user_id] if item['product_id'] != product_id]
    
    return jsonify(CARTS.get(user_id, []))

@app.route('/<path:path>')
def catch_all(path):
    """A special route that catches all other requests"""
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create static/images directory if it doesn't exist
    os.makedirs(os.path.join(app.static_folder, 'images'), exist_ok=True)
    app.run(debug=True)