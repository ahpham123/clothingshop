from flask import Flask, redirect, url_for, render_template, jsonify, request
import json
import os
import requests

# Our Flask app object
app = Flask(__name__, template_folder='../templates',
            static_folder='../static')

#API call for products
PRODUCTS = requests.get('https://fakestoreapi.com/products')
'''
[
  {
    "id": 0,
    "title": "string",
    "price": 0.1,
    "description": "string",
    "category": "string",
    "image": "http://example.com"
    "rating": {"rate": 4, "count": 150 }
  }
]
'''

# In-memory "database" for cart (in production, use a real database)
CARTS = []
'''
[
    {
        "user_id": 0,
        "product_id": 0,
        "quantity": 0
    }
]
'''

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
    for item in PRODUCTS:
            if item["id"] == product_id:
                return item
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/cart', methods=['GET'])
def get_cart(user_id):
    """API endpoint for cart operations"""
    if not user_id:
        return jsonify({"error": "User id expected not found"}), 404
    
    if request.method == 'GET':
        if user_id not in CARTS:
            CARTS[user_id] = {}
            return CARTS[user_id]
    
        # Get user's cart (in a real app, you'd have user authentication)
        return CARTS[user_id]

@app.route('/api/cart', methods=['POST'])
def add_cart(user_id, product_id):

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
        
    if request.method == 'POST':
        #Make user cart if doesnt exist
        if user_id not in CARTS:
            CARTS[user_id] = {}

        # Add item to cart
        for item in PRODUCTS:
            if item["id"] == product_id:
                #Instead of set quantity, make it add to stored quantity ------------------------------------------------------------------------
                CARTS[user_id] = {product_id: 1}
                return jsonify({"success": "Product found and added"}), 200
        
        return jsonify({"error": "Product not found"}), 404

        

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart(user_id, product_id):
    """API endpoint to remove item from cart"""
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    
    if user_id in CARTS:
        CARTS[user_id] = [item for item in CARTS[user_id] if item['product_id'] != product_id]
    
    return jsonify(CARTS.get(user_id, []))

@app.route('/<path:path>')
def catch_all(path):
    """A special route that catches all other requests"""
    return redirect(url_for('index'))

# ===== Vercel-Specific Additions =====
@app.route('/api/search')
def search():
    """Example API endpoint"""
    return jsonify({"message": "Search endpoint works!"})

def vercel_handler(request):
    """Required for Vercel serverless functions"""
    with app.app_context():
        response = app.full_dispatch_request()()
    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": response.get_data(as_text=True)
    }

if __name__ == '__main__':
    # Create static/images directory if it doesn't exist
    os.makedirs(os.path.join(app.static_folder, 'images'), exist_ok=True)
    app.run(debug=True)
else:
    # This makes it work both locally and on Vercel
    app = app