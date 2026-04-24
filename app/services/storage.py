import boto3
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from botocore.exceptions import ClientError
from ..models import TelemetryRecord, SummaryResponse

class StorageError(Exception):
    """Base exception for storage operations."""
    pass

class RecordNotFoundError(StorageError):
    """Raised when a record is not found in DynamoDB."""
    pass

# AWS client getters to ensure they are created within the mock context if needed
def get_s3_client():
    return boto3.client('s3')

def get_dynamodb_resource():
    return boto3.resource('dynamodb', region_name=os.environ.get("AWS_REGION", "us-east-1"))

async def save_telemetry(record: TelemetryRecord, bucket_name: str, table_name: str):
    """
    Saves raw telemetry JSON to S3 and metadata to DynamoDB.
    """
    try:
        s3 = get_s3_client()
        dynamodb = get_dynamodb_resource()
        
        # Save raw JSON to S3
        s3_key = f"telemetry/{record.vehicle_id}/{record.timestamp.isoformat()}.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=record.model_dump_json()
        )
        
        # Save metadata to DynamoDB
        # Convert floats to Decimal for DynamoDB compatibility
        table = dynamodb.Table(table_name)
        table.put_item(
            Item={
                'vehicle_id': record.vehicle_id,
                'timestamp': record.timestamp.isoformat(),
                'speed_kmh': Decimal(str(record.speed_kmh)),
                'engine_temp_celsius': Decimal(str(record.engine_temp_celsius)),
                'mileage_km': record.mileage_km,
                'fault_codes': record.fault_codes,
                'data_type': 'telemetry'
            }
        )
    except ClientError as e:
        raise StorageError(f"Failed to save telemetry: {str(e)}")

async def save_summary(summary: SummaryResponse, table_name: str):
    """
    Saves AI-generated summary to DynamoDB.
    """
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(table_name)
        table.put_item(
            Item={
                'vehicle_id': summary.vehicle_id,
                'summary': summary.summary,
                'severity': summary.severity,
                'data_type': 'summary',
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        )
    except ClientError as e:
        raise StorageError(f"Failed to save summary: {str(e)}")

async def get_summary(vehicle_id: str, table_name: str) -> SummaryResponse:
    """
    Fetches the stored summary from DynamoDB by vehicle_id.
    """
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'vehicle_id': vehicle_id})
        
        item = response.get('Item')
        if not item or item.get('data_type') != 'summary':
            raise RecordNotFoundError(f"No summary found for vehicle {vehicle_id}")
            
        return SummaryResponse(
            vehicle_id=item['vehicle_id'],
            summary=item['summary'],
            severity=item['severity']
        )
    except ClientError as e:
        raise StorageError(f"Failed to fetch summary: {str(e)}")
