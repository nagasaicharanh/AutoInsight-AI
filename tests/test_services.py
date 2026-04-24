import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from app.services.ai import analyze_telemetry
from app.models import TelemetryRecord, SummaryResponse

@pytest.mark.asyncio
async def test_analyze_telemetry_success(mocker):
    """Tests successful telemetry analysis using mocked Groq client."""
    # Mock the AsyncGroq client
    mock_client = mocker.patch("app.services.ai.client")
    
    # Mock the response from Groq
    mock_completion = mocker.Mock()
    mock_completion.choices = [
        mocker.Mock(message=mocker.Mock(content='{"vehicle_id": "v123", "summary": "Everything looks great.", "severity": "LOW"}'))
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
    
    telemetry = TelemetryRecord(
        vehicle_id="v123",
        timestamp=datetime.now(),
        fault_codes=[],
        speed_kmh=60.0,
        engine_temp_celsius=90.0,
        mileage_km=10000
    )
    
    result = await analyze_telemetry(telemetry)
    
    assert result.vehicle_id == "v123"
    assert result.summary == "Everything looks great."
    assert result.severity == "LOW"
    assert mock_client.chat.completions.create.called

@pytest.mark.asyncio
async def test_analyze_telemetry_failure(mocker):
    """Tests fallback handling when Groq API fails."""
    # Mock the AsyncGroq client to raise an exception
    mock_client = mocker.patch("app.services.ai.client")
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
    
    telemetry = TelemetryRecord(
        vehicle_id="v123",
        timestamp=datetime.now(),
        fault_codes=[],
        speed_kmh=60.0,
        engine_temp_celsius=90.0,
        mileage_km=10000
    )
    
    result = await analyze_telemetry(telemetry)
    
    assert result.vehicle_id == "v123"
    assert "Error analyzing telemetry" in result.summary
    assert result.severity == "LOW"
