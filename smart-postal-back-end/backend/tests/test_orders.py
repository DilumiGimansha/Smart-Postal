import pytest
from fastapi import status

def test_create_order(client, auth_headers):
    """Test creating an order"""
    response = client.post(
        "/api/orders/",
        headers=auth_headers,
        json={
            "delivery_address": "123 Main Street, Apt 4B",
            "delivery_city": "New York",
            "delivery_postal_code": "10001",
            "delivery_instructions": "Ring doorbell twice",
            "total_amount": 99.99,
            "verification_required": True
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["delivery_city"] == "New York"
    assert data["total_amount"] == 99.99
    assert data["status"] == "pending"
    assert "order_number" in data

def test_list_orders(client, auth_headers):
    """Test listing orders"""
    # Create an order first
    client.post(
        "/api/orders/",
        headers=auth_headers,
        json={
            "delivery_address": "123 Main St",
            "delivery_city": "Boston",
            "delivery_postal_code": "02101",
            "total_amount": 50.00
        }
    )
    
    # List orders
    response = client.get("/api/orders/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["delivery_city"] == "Boston"

def test_get_order_by_id(client, auth_headers):
    """Test getting order by ID"""
    # Create order
    create_response = client.post(
        "/api/orders/",
        headers=auth_headers,
        json={
            "delivery_address": "456 Oak Ave",
            "delivery_city": "Chicago",
            "delivery_postal_code": "60601",
            "total_amount": 75.50
        }
    )
    order_id = create_response.json()["id"]
    
    # Get order
    response = client.get(f"/api/orders/{order_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == order_id
    assert data["delivery_city"] == "Chicago"

def test_update_order_instructions(client, auth_headers):
    """Test updating order delivery instructions"""
    # Create order
    create_response = client.post(
        "/api/orders/",
        headers=auth_headers,
        json={
            "delivery_address": "789 Pine St",
            "delivery_city": "Seattle",
            "delivery_postal_code": "98101",
            "total_amount": 120.00
        }
    )
    order_id = create_response.json()["id"]
    
    # Update instructions
    response = client.put(
        f"/api/orders/{order_id}",
        headers=auth_headers,
        json={
            "delivery_instructions": "Leave at front desk"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["delivery_instructions"] == "Leave at front desk"

def test_get_biometric_status(client, auth_headers):
    """Test getting biometric status"""
    # Create order
    create_response = client.post(
        "/api/orders/",
        headers=auth_headers,
        json={
            "delivery_address": "321 Elm St",
            "delivery_city": "Portland",
            "delivery_postal_code": "97201",
            "total_amount": 45.00
        }
    )
    order_id = create_response.json()["id"]
    
    # Get biometric status
    response = client.get(
        f"/api/orders/{order_id}/biometric-status",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["order_id"] == order_id
    assert "voice_enrolled" in data
    assert "fingerprint_enrolled" in data
