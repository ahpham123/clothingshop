import pytest
from flask import Flask
import os
import sys
from dotenv import load_dotenv
import json
from supabase import create_client

# Add the parent directory to the path so we can import the app
# Adjust this path to point to where your Flask app file is located
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import your Flask app - adjust this import based on your actual file structure
from api.index import app as flask_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Load environment variables
    load_dotenv()
    
    # Create the app with testing config
    test_app = flask_app
    test_app.config.update({
        "TESTING": True,
    })
    
    # Return test app
    return test_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing without actually hitting the database."""
    # This would usually be replaced with a proper mock
    pass