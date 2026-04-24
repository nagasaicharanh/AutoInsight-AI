import os
import json
from groq import AsyncGroq
from ..models import TelemetryRecord, SummaryResponse

# Initialize AsyncGroq client
# Ensure GROQ_API_KEY is set in environment variables
client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

async def analyze_telemetry(telemetry: TelemetryRecord) -> SummaryResponse:
    """
    Analyzes vehicle telemetry using Groq's LLM to assess fault severity.
    Returns a SummaryResponse with the assessment.
    """
    prompt = f"""
    Analyze the following vehicle telemetry data and provide a summary of potential issues and their severity.
    
    Vehicle ID: {telemetry.vehicle_id}
    Timestamp: {telemetry.timestamp}
    Fault Codes: {', '.join(telemetry.fault_codes)}
    Speed: {telemetry.speed_kmh} km/h
    Engine Temp: {telemetry.engine_temp_celsius} °C
    Mileage: {telemetry.mileage_km} km

    Return the analysis in structured JSON format with the following keys:
    - vehicle_id: "{telemetry.vehicle_id}"
    - summary: A concise explanation of the vehicle health.
    - severity: One of 'LOW', 'MEDIUM', or 'HIGH'.
    """

    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior automotive diagnostic assistant. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
        
        response_content = chat_completion.choices[0].message.content
        response_data = json.loads(response_content)
        
        return SummaryResponse.model_validate(response_data)
        
    except Exception as e:
        # Fallback error handling
        return SummaryResponse(
            vehicle_id=telemetry.vehicle_id,
            summary=f"Error analyzing telemetry: {str(e)}",
            severity="LOW"
        )
