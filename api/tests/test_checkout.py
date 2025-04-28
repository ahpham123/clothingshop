import json
import pytest
from unittest.mock import patch, MagicMock

def test_checkout_success(client):
    """Test successful checkout process."""
    # Mock data
    mock_items = [
        {
            'product_id': 1,
            'title': 'Test Product',
            'price': 19.99,
            'quantity': 2
        }
    ]
    
    # Mock the Supabase responses
    mock_user_response = MagicMock()
    mock_user_response.data = [{'user_id': 'test_user'}]
    mock_user_response.error = None
    
    mock_order_response = MagicMock()
    mock_order_response.data = [{'id': 123}]
    mock_order_response.error = None
    
    # Patch the supabase client's execute methods
    with patch('api.index.supabase.table') as mock_table:
        # Configure the mock for users table
        mock_table_users = MagicMock()
        mock_table_users.upsert.return_value.execute.return_value = mock_user_response
        
        # Configure the mock for orders table
        mock_table_orders = MagicMock()
        mock_table_orders.insert.return_value.execute.return_value = mock_order_response
        
        # Set up the mock table method to return different mocks based on table name
        def side_effect(table_name):
            if table_name == 'users':
                return mock_table_users
            elif table_name == 'orders':
                return mock_table_orders
        
        mock_table.side_effect = side_effect
        
        # Make request to checkout endpoint
        response = client.post('/api/checkout', 
                             json={
                                 'user_id': 'test_user',
                                 'items': mock_items
                             },
                             content_type='application/json')
        data = json.loads(response.data)
        
        # Assertions
        assert response.status_code == 200
        assert data['success'] == True
        assert data['order_id'] == 123

def test_checkout_with_uuid_generation(client):
    """Test checkout with UUID generation for legacy user IDs."""
    # Mock data
    mock_items = [
        {
            'product_id': 1,
            'title': 'Test Product',
            'price': 19.99,
            'quantity': 1
        }
    ]
    
    # Mock the Supabase responses
    mock_user_response = MagicMock()
    mock_user_response.data = [{'user_id': 'new-uuid'}]
    mock_user_response.error = None
    
    mock_order_response = MagicMock()
    mock_order_response.data = [{'id': 124}]
    mock_order_response.error = None
    
    # Patch the supabase client and uuid generation
    with patch('api.index.supabase.table') as mock_table, \
         patch('uuid.uuid4', return_value='new-uuid'):
        
        # Configure the mocks
        mock_table_users = MagicMock()
        mock_table_users.upsert.return_value.execute.return_value = mock_user_response
        
        mock_table_orders = MagicMock()
        mock_table_orders.insert.return_value.execute.return_value = mock_order_response
        
        # Set up the mock table method
        def side_effect(table_name):
            if table_name == 'users':
                return mock_table_users
            elif table_name == 'orders':
                return mock_table_orders
        
        mock_table.side_effect = side_effect
        
        # Make request with legacy user ID format
        response = client.post('/api/checkout', 
                             json={
                                 'user_id': 'user_123',
                                 'items': mock_items
                             },
                             content_type='application/json')
        data = json.loads(response.data)
        
        # Assertions
        assert response.status_code == 200
        assert data['success'] == True
        assert 'new_user_id' in data
        assert data['new_user_id'] == 'new-uuid'

def test_checkout_error_handling(client):
    """Test error handling during checkout."""
    # Mock data
    mock_items = [
        {
            'product_id': 1,
            'title': 'Test Product',
            'price': 19.99,
            'quantity': 1
        }
    ]
    
    # Mock a failed Supabase response
    mock_error_response = MagicMock()
    mock_error_response.error = "Database error"
    
    # Patch the supabase client
    with patch('api.index.supabase.table') as mock_table:
        mock_table.return_value.upsert.return_value.execute.return_value = mock_error_response
        
        # Make request to checkout endpoint
        response = client.post('/api/checkout', 
                             json={
                                 'user_id': 'test_user',
                                 'items': mock_items
                             },
                             content_type='application/json')
        data = json.loads(response.data)
        
        # Assertions
        assert response.status_code == 500
        assert 'error' in data