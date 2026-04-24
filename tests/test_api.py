import pytest
from datetime import datetime
from app.models import SummaryResponse

def test_health_check(test_client):
    """GET /health returns 200."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ingest_valid_telemetry(test_client, mocker):
    """POST /ingest with valid payload returns 200 + SummaryResponse shape."""
    # Mock AI service
    mock_summary = SummaryResponse(
        vehicle_id="v123",
        summary="Engine temperature is slightly high, but overall health is good.",
        severity="LOW"
    )
    mocker.patch("app.main.analyze_telemetry", return_value=mock_summary)
    
    payload = {
        "vehicle_id": "v123",
        "timestamp": datetime.now().isoformat(),
        "fault_codes": ["P0101"],
        "speed_kmh": 65.5,
        "engine_temp_celsius": 98.0,
        "mileage_km": 15000
    }
    
    response = test_client.post("/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_id"] == "v123"
    assert "summary" in data
    assert data["severity"] == "LOW"

def test_ingest_invalid_payload(test_client):
    """POST /ingest with missing fields returns 422."""
    payload = {
        "vehicle_id": "v123"
        # missing other fields
    }
    response = test_client.post("/ingest", json=payload)
    assert response.status_code == 422

def test_get_summary_exists(test_client, mocker):
    """GET /summary/{id} for existing record returns correct data."""
    # First ingest to create the summary
    mock_summary = SummaryResponse(
        vehicle_id="v456",
        summary="All systems nominal.",
        severity="LOW"
    )
    mocker.patch("app.main.analyze_telemetry", return_value=mock_summary)
    
    ingest_payload = {
        "vehicle_id": "v456",
        "timestamp": datetime.now().isoformat(),
        "fault_codes": [],
        "speed_kmh": 0.0,
        "engine_temp_celsius": 20.0,
        "mileage_km": 500
    }
    test_client.post("/ingest", json=ingest_payload)
    
    # Now fetch it
    response = test_client.get("/summary/v456")
    assert response.status_code == 200
    assert response.json()["vehicle_id"] == "v456"
    assert response.json()["summary"] == "All systems nominal."

def test_get_summary_not_found(test_client):
    """GET /summary/{id} for unknown id returns 404."""
    response = test_client.get("/summary/unknown_vehicle")
    assert response.status_code == 404
    assert "no summary found" in response.json()["detail"].lower()
