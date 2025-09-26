#!/usr/bin/env python3
"""Debug script to test TestClient creation."""

import sys
import traceback

def test_testclient():
    try:
        print("Testing TestClient creation...")
        
        # Import the app
        from main import app
        print("✓ App imported successfully")
        
        # Try FastAPI TestClient
        from fastapi.testclient import TestClient
        print("✓ FastAPI TestClient imported")
        
        # Create client
        client = TestClient(app)
        print("✓ TestClient created successfully")
        
        # Test a simple request
        response = client.get("/health")
        print(f"✓ Health check response: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_testclient()
    sys.exit(0 if success else 1)