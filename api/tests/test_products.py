import json
import pytest
from unittest.mock import patch, MagicMock

def test_get_products(client, monkeypatch):
    """Test the /api/products endpoint."""
    # Mock data that would come from Supabase
    mock_products = [
        {
            'id': 1,
            'title': 'Test Product',
            'price': 19.99,
            'description': 'Test description',
            'category': 'test',
            'image': 'test.jpg',
            'rating.rate': 4.5,
            'rating.count': 120
        }
    ]
    
    # Mock the Supabase response
    mock_response = MagicMock()
    mock_response.data = mock_products
    mock_response.error = None
    
    # Patch the supabase client's execute method
    with patch('api.index.supabase.table') as mock_table:
        mock_table.return_value.select.return_value.execute.return_value = mock_response
        
        # Make request to the endpoint
        response = client.get('/api/products')
        data = json.loads(response.data)
        
        # Assertions
        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]['title'] == 'Test Product'
        assert data[0]['rating']['rate'] == 4.5

def test_get_product_by_id(client, monkeypatch):
    """Test the /api/products/<id> endpoint."""
    # Mock data for a single product
    mock_product = {
        'id': 1,
        'title': 'Test Product',
        'price': 19.99,
        'description': 'Test description',
        'category': 'test',
        'image': 'test.jpg'
    }
    
    # Mock the Supabase response
    mock_response = MagicMock()
    mock_response.data = [mock_product]
    mock_response.error = None
    
    # Patch the supabase client's execute method
    with patch('api.index.supabase.table') as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Make request to the endpoint
        response = client.get('/api/products/1')
        data = json.loads(response.data)
        
        # Assertions
        assert response.status_code == 200
        assert data['id'] == 1
        assert data['title'] == 'Test Product'

def test_get_product_not_found(client, monkeypatch):
    """Test the /api/products/<id> endpoint with non-existent ID."""
    # Mock an empty response
    mock_response = MagicMock()
    mock_response.data = []
    mock_response.error = None
    
    # Patch the supabase client's execute method
    with patch('api.index.supabase.table') as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Make request to the endpoint
        response = client.get('/api/products/999')
        data = json.loads(response.data)
        
        # Assertions
        assert response.status_code == 404
        assert 'error' in data