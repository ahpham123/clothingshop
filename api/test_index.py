import pytest
import json
import uuid
from unittest.mock import patch, MagicMock

# Import the Flask application from index.py instead of app.py
from index import app as flask_app

@pytest.fixture
def app():
    """Create a Flask test client fixture for our tests"""
    # Configure app for testing
    flask_app.config.update({
        "TESTING": True,
    })
    
    # Return test client
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client

# Mock response class to simulate Supabase responses
class MockSupabaseResponse:
    def __init__(self, data=None, error=None):
        self.data = data if data is not None else []
        self.error = error

# Tests for the pages/routes
def test_index_route(app):
    """Test the index route returns the correct template"""
    response = app.get('/')
    assert response.status_code == 200

def test_products_route(app):
    """Test the products route returns the correct template"""
    response = app.get('/products')
    assert response.status_code == 200

def test_cart_route(app):
    """Test the cart route returns the correct template"""
    response = app.get('/cart')
    assert response.status_code == 200

def test_nonexistent_route_redirects(app):
    """Test that nonexistent routes redirect to index"""
    response = app.get('/nonexistent-path')
    assert response.status_code == 302  # Redirect code

# Tests for the API endpoints
@patch('index.supabase')
def test_get_products_success(mock_supabase, app):
    """Test successfully retrieving products"""
    # Setup mock response
    mock_products = [
        {
            'id': 1,
            'title': 'Test Product',
            'price': 19.99,
            'description': 'Test description',
            'category': 'test',
            'image': 'test.jpg',
            'rating.rate': 4.5,
            'rating.count': 10
        }
    ]
    
    mock_response = MockSupabaseResponse(data=mock_products)
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response
    
    # Make request
    response = app.get('/api/products')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Test Product'
    assert data[0]['rating']['rate'] == 4.5
    assert data[0]['rating']['count'] == 10

@patch('index.supabase')
def test_get_products_error(mock_supabase, app):
    """Test error handling when retrieving products fails"""
    # Setup mock response with error
    mock_response = MockSupabaseResponse(error="Database error")
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response
    
    # Make request
    response = app.get('/api/products')
    
    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data

@patch('index.supabase')
def test_get_product_by_id_success(mock_supabase, app):
    """Test successfully retrieving a single product by ID"""
    # Setup mock response
    mock_product = {
        'id': 1,
        'title': 'Test Product',
        'price': 19.99,
        'description': 'Test description',
        'category': 'test',
        'image': 'test.jpg'
    }
    
    mock_response = MockSupabaseResponse(data=[mock_product])
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
    
    # Make request
    response = app.get('/api/products/1')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Test Product'

@patch('index.supabase')
def test_get_product_by_id_not_found(mock_supabase, app):
    """Test 404 response when product is not found"""
    # Setup mock response with empty data
    mock_response = MockSupabaseResponse(data=[])
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
    
    # Make request
    response = app.get('/api/products/999')
    
    # Check response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data

def test_get_cart_empty(app):
    """Test getting an empty cart"""
    response = app.get('/api/cart?user_id=test_user')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_cart_no_user_id(app):
    """Test error when no user_id is provided"""
    response = app.get('/api/cart')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

@patch('index.supabase')
def test_add_to_cart_new_item(mock_supabase, app):
    """Test adding a new item to cart"""
    # Setup mock product response
    mock_product = {
        'id': 1,
        'title': 'Test Product',
        'price': 19.99,
        'image': 'test.jpg'
    }
    
    mock_response = MockSupabaseResponse(data=[mock_product])
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
    
    # Make request
    response = app.post('/api/cart/add', 
                       json={'user_id': 'test_user', 'product_id': 1},
                       content_type='application/json')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert len(data['cart']) == 1
    assert data['cart'][0]['product_id'] == 1
    assert data['cart'][0]['quantity'] == 1

@patch('index.supabase')
def test_add_to_cart_existing_item(mock_supabase, app):
    """Test adding an existing item to cart (should increment quantity)"""
    # First add an item
    mock_product = {
        'id': 1,
        'title': 'Test Product',
        'price': 19.99,
        'image': 'test.jpg'
    }
    
    mock_response = MockSupabaseResponse(data=[mock_product])
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
    
    app.post('/api/cart/add', 
            json={'user_id': 'test_user2', 'product_id': 1},
            content_type='application/json')
    
    # Then add the same item again
    response = app.post('/api/cart/add', 
                       json={'user_id': 'test_user2', 'product_id': 1},
                       content_type='application/json')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert len(data['cart']) == 1
    assert data['cart'][0]['quantity'] == 2

def test_remove_from_cart(app):
    """Test removing an item from cart"""
    # First add an item using the test client
    with patch('index.supabase') as mock_supabase:
        mock_product = {
            'id': 5,
            'title': 'Remove Test',
            'price': 29.99,
            'image': 'remove.jpg'
        }
        
        mock_response = MockSupabaseResponse(data=[mock_product])
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        app.post('/api/cart/add', 
                json={'user_id': 'test_user3', 'product_id': 5},
                content_type='application/json')
    
    # Then remove the item
    response = app.post('/api/cart/remove',
                        json={'user_id': 'test_user3', 'product_id': 5},
                        content_type='application/json')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert len(data['cart']) == 0

@patch('index.supabase')
def test_checkout_success(mock_supabase, app):
    """Test successful checkout process"""
    # Setup mock responses
    user_response = MockSupabaseResponse(data=[{"user_id": "test_user4"}])
    order_response = MockSupabaseResponse(data=[{"id": 123}])
    
    # Configure mock to return different responses for different tables
    def side_effect_table(table_name):
        mock_table = MagicMock()
        
        if table_name == 'users':
            mock_table.upsert.return_value.execute.return_value = user_response
        elif table_name == 'orders':
            mock_table.insert.return_value.execute.return_value = order_response
            
        return mock_table
    
    mock_supabase.table.side_effect = side_effect_table
    
    # Make request
    cart_items = [{"product_id": 1, "title": "Test", "price": 19.99, "quantity": 2}]
    response = app.post('/api/checkout',
                        json={'user_id': 'test_user4', 'items': cart_items},
                        content_type='application/json')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['order_id'] == 123

@patch('index.supabase')
def test_checkout_with_uuid_conversion(mock_supabase, app):
    """Test checkout with user_id in old format gets converted to UUID"""
    # Setup mock responses
    user_response = MockSupabaseResponse(data=[{"user_id": "some-uuid"}])
    order_response = MockSupabaseResponse(data=[{"id": 456}])
    
    # Configure mock
    def side_effect_table(table_name):
        mock_table = MagicMock()
        
        if table_name == 'users':
            mock_table.upsert.return_value.execute.return_value = user_response
        elif table_name == 'orders':
            mock_table.insert.return_value.execute.return_value = order_response
            
        return mock_table
    
    mock_supabase.table.side_effect = side_effect_table
    
    # Make request with old format user_id
    cart_items = [{"product_id": 2, "title": "Test2", "price": 29.99, "quantity": 1}]
    response = app.post('/api/checkout',
                        json={'user_id': 'user_oldformat', 'items': cart_items},
                        content_type='application/json')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'new_user_id' in data
    assert uuid.UUID(data['new_user_id'], version=4)  # Verify it's a valid UUID