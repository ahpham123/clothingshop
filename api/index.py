from flask import Flask, redirect, url_for, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import requests
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Our Flask app object
app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# In-memory "database" for cart (in production, use a real database)
CARTS = {}

@app.route('/')
@app.route('/index')
def index():
    """Our default routes of '/' and '/index'"""
    return render_template('index.html')

@app.route('/products')
def products():
    """Products page route"""
    return render_template('products.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    """API endpoint to get all products from Supabase"""
    try:
        # Fetch products from Supabase
        response = supabase.table('products').select('*').execute()
        
        # Check if there was an error
        if hasattr(response, 'error') and response.error is not None:
            return jsonify({"error": "Failed to fetch products from database"}), 500
            
        products = response.data
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch products: {str(e)}"}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """API endpoint to get a single product by ID from Supabase"""
    try:
        response = supabase.table('products').select('*').eq('id', product_id).execute()
        
        if hasattr(response, 'error') and response.error is not None:
            return jsonify({"error": "Failed to fetch product from database"}), 500
            
        if not response.data:
            return jsonify({"error": "Product not found"}), 404
            
        product = response.data[0]
        return jsonify(product)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch product: {str(e)}"}), 500

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """API endpoint to get user's cart"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    # Return empty cart if user doesn't have one yet
    if user_id not in CARTS:
        CARTS[user_id] = []
    
    return jsonify(CARTS[user_id])

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """API endpoint to add item to cart"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    
    if not user_id or not product_id:
        return jsonify({"error": "User ID and Product ID are required"}), 400
    
    # Initialize cart if it doesn't exist
    if user_id not in CARTS:
        CARTS[user_id] = []
    
    # Check if product is already in cart
    for item in CARTS[user_id]:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            return jsonify({"success": True, "cart": CARTS[user_id]})
    
    # Add new item to cart
    try:
        # Fetch product details from Supabase
        response = supabase.table('products').select('*').eq('id', product_id).execute()
        
        if hasattr(response, 'error') and response.error is not None:
            return jsonify({"error": "Failed to fetch product from database"}), 500
            
        if not response.data:
            return jsonify({"error": "Product not found"}), 404
            
        product = response.data[0]
        
        # Add to cart with quantity 1
        CARTS[user_id].append({
            'product_id': product_id,
            'title': product['title'],
            'price': product['price'],
            'image': product['image'],
            'quantity': 1
        })
        
        return jsonify({"success": True, "cart": CARTS[user_id]})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch product: {str(e)}"}), 500

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    """API endpoint to remove item from cart"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    
    if not user_id or not product_id:
        return jsonify({"error": "User ID and Product ID are required"}), 400
    
    if user_id in CARTS:
        CARTS[user_id] = [item for item in CARTS[user_id] if item['product_id'] != product_id]
    
    return jsonify({"success": True, "cart": CARTS.get(user_id, [])})

# Admin endpoint to seed the database with products
@app.route('/api/admin/seed-products', methods=['POST'])
def seed_products():
    """Admin endpoint to seed the Supabase database with products from FakeStoreAPI"""
    # Optional: Add authentication for this endpoint
    
    try:
        # First check if products already exist
        existing = supabase.table('products').select('id').limit(1).execute()
        
        if existing.data and len(existing.data) > 0:
            return jsonify({"message": "Database already contains products"}), 200
        
        # Fetch products from FakeStoreAPI
        response = requests.get('https://fakestoreapi.com/products')
        response.raise_for_status()
        products = response.json()
        
        # Transform the products to match our schema
        transformed_products = []
        for product in products:
            transformed_products.append({
                'id': product['id'],
                'title': product['title'],
                'price': product['price'],
                'description': product['description'],
                'category': product['category'],
                'image': product['image'],
                'rating_rate': product['rating']['rate'],
                'rating_count': product['rating']['count']
            })
        
        # Insert products into Supabase
        for product in transformed_products:
            supabase.table('products').insert(product).execute()
        
        return jsonify({"success": True, "message": f"Added {len(transformed_products)} products to database"})
    except Exception as e:
        return jsonify({"error": f"Failed to seed database: {str(e)}"}), 500

@app.route('/<path:path>')
def catch_all(path):
    """A special route that catches all other requests"""
    return redirect(url_for('index'))

# ===== Vercel-Specific Additions =====
def vercel_handler(request):
    """Required for Vercel serverless functions"""
    with app.test_request_context(
        path=request.get('path', '/'),
        method=request.get('httpMethod', 'GET'),
        headers=request.get('headers', {}),
        data=request.get('body', '')
    ):
        try:
            response = app.full_dispatch_request()
        except Exception as e:
            return {
                "statusCode": 500,
                "body": str(e)
            }
            
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