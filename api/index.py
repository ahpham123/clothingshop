from flask import Flask, redirect, url_for, render_template, jsonify, request
from flask_cors import CORS
import os
from supabase import create_client
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Our Flask app object
app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# In-memory "database" for cart (to keep things simple)
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

@app.route('/cart')
def cart():
    """Cart page route"""
    return render_template('cart.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        search_query = request.args.get('search', '').strip()
        
        query = supabase.table('products').select('*')
        
        if search_query:
            query = query.ilike('title', f'%{search_query}%')
        
        response = query.execute()
        
        if hasattr(response, 'error') and response.error is not None:
            return jsonify({"error": "Failed to fetch products"}), 500
            
        products = response.data
        
        transformed_products = []
        for product in products:
            transformed_product = {
                'id': product['id'],
                'title': product['title'],
                'price': product['price'],
                'description': product['description'],
                'category': product['category'],
                'image': product['image'],
                'rating': {
                    'rate': product.get('rating.rate', 0),
                    'count': product.get('rating.count', 0)
                }
            }
            transformed_products.append(transformed_product)
        
        return jsonify(transformed_products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """API endpoint to process checkout and save to Supabase"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user_id = data.get('user_id')
    items = data.get('items')
    
    if not user_id or not items:
        return jsonify({"error": "User ID and Items are required"}), 400
    
    try:
        # Check if user_id is in the old format and convert if needed
        if user_id.startswith('user_'):
            # For existing users with the old format, generate a new UUID
            user_id = str(uuid.uuid4())
            # Return the new UUID so frontend can update localStorage
            new_uuid_generated = True
        else:
            new_uuid_generated = False
        
        # First, add to users table
        user_response = supabase.table('users').upsert(
            {"user_id": user_id}
        ).execute()
        
        if hasattr(user_response, 'error') and user_response.error is not None:
            return jsonify({"error": f"Failed to create user entry: {user_response.error}"}), 500
        
        # Then add to orders table with the items JSON
        order_response = supabase.table('orders').insert({
            "user_id": user_id,
            "items": items
        }).execute()
        
        if hasattr(order_response, 'error') and order_response.error is not None:
            return jsonify({"error": f"Failed to create order entry: {order_response.error}"}), 500
        
        # Clear the cart after successful checkout
        if user_id in CARTS:
            CARTS[user_id] = []
        
        response_data = {
            "success": True, 
            "message": "Order processed successfully",
            "order_id": order_response.data[0]['id'] if order_response.data else None
        }
        
        # If we generated a new UUID, include it in the response
        if new_uuid_generated:
            response_data["new_user_id"] = user_id
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": f"Checkout failed: {str(e)}"}), 500

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