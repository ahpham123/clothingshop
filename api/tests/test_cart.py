import json
import pytest
from unittest.mock import patch, MagicMock

def test_get_cart_empty(client):
    """Test getting an empty cart."""
    response = client.get('/api/cart?user_id=test_user')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data == []

def test_add_to_cart(client):
    """Test adding an item to the cart."""
    # Mock product data that would be returned by Supabase
    mock_product = {
        'id':1,
        'title': 'Test Product',
        'price': 19.99,
        'image': 'test.jpg'
    }
    
    # Mock the Supabase response
    mock_response = MagicMock()
    mock_response.data = [mock_product]
    mock_response.error = None
    
    # Patch the supabase client's execute method
    with patch('api.index.supabase.table') as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Make request to add item to cart
        response = client.post('/api/cart/add', 
                            json={
                                'user_id': 'test_user',
                                'product_id': 1
                            },
                            content_type='application/json')
        data = json.loads(response.data)
        
        # Assertions
        assert response.status_code == 200
        assert data['success'] == True
        assert len(data['cart']) == 1
        assert data['cart'][0]['product_id'] == 1
        assert data['cart'][0]['quantity'] == 1

def test_add_to_cart_increment_quantity(client):
    """Test adding the same item to cart twice increments quantity."""
    # Mock product data
    mock_product = {
        'id': 1,
        'title': 'Test Product',
        'price': 19.99,
        'image': 'test.jpg'
    }
    
    # Mock the Supabase response
    mock_response = MagicMock()
    mock_response.data = [mock_product]
    mock_response.error = None
    
    # Patch the supabase client's execute method
    with patch('api.index.supabase.table') as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Add item to cart first time
        client.post('/api/cart/add', 
                  json={
                      'user_id': 'test_user2',
                      'product_id': 1
                  },
                  content_type='application/json')
        
        # Add same item again
        response = client.post('/api/cart/add', 
                            json={
                                'user_id': 'test_user2',
                                'product_id': 1
                            },
                            content_type='application/json')
        data = json.loads(response.data)
        
        # Assertions
        assert response.status_code == 200
        assert data['cart'][0]['quantity'] == 2

def test_remove_from_cart(client):
    """Test removing an item from the cart."""
    # First add an item
    with patch('api.index.supabase.table') as mock_table:
        mock_product = {
            'id': 1,
            'title': 'Test Product',
            'price': 19.99,
            'image': 'test.jpg'
        }
        mock_response = MagicMock()
        mock_response.data = [mock_product]
        mock_response.error = None
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        client.post('/api/cart/add', 
                  json={
                      'user_id': 'test_user3',
                      'product_id': 1
                  },
                  content_type='application/json')
    
    # Then remove it
    response = client.post('/api/cart/remove', 
                         json={
                             'user_id': 'test_user3',
                             'product_id': 1
                         },
                         content_type='application/json')
    data = json.loads(response.data)
    
    # Assertions
    assert response.status_code == 200
    assert data['success'] == True
    assert len(data['cart']) == 0