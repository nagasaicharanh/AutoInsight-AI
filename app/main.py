import os
from fastapi import FastAPI, HTTPException, Depends
from mangum import Mangum
from .models import TelemetryRecord, SummaryResponse
from .services.ai import analyze_telemetry
from .services import storage

app = FastAPI(title="AutoInsight AI Telemetry Ingestion")

# Configuration from environment variables
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "autoinsight-telemetry")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE_NAME", "autoinsight-summaries")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/ingest", response_model=SummaryResponse)
async def ingest_telemetry(record: TelemetryRecord):
    """
    Ingests vehicle telemetry, saves to AWS storage, and triggers AI analysis.
    """
    try:
        # 1. Save raw telemetry and metadata
        await storage.save_telemetry(record, S3_BUCKET, DYNAMODB_TABLE)
        
        # 2. Trigger AI analysis
        summary = await analyze_telemetry(record)
        
        # 3. Save AI summary to DynamoDB
        await storage.save_summary(summary, DYNAMODB_TABLE)
        
        return summary
        
    except storage.StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/summary/{vehicle_id}", response_model=SummaryResponse)
async def get_vehicle_summary(vehicle_id: str):
    """
    Retrieves the stored summary for a specific vehicle.
    """
    try:
        summary = await storage.get_summary(vehicle_id, DYNAMODB_TABLE)
        return summary
    except storage.RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except storage.StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mangum handler for AWS Lambda compatibility
handler = Mangum(app)
