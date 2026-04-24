import os
import pytest
import boto3
from moto import mock_aws
from fastapi.testclient import TestClient

# Set dummy environment variables before importing the app
os.environ["GROQ_API_KEY"] = "testing"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["S3_BUCKET_NAME"] = "autoinsight-telemetry"
os.environ["DYNAMODB_TABLE_NAME"] = "autoinsight-summaries"

from app.main import app

@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    pass

@pytest.fixture(autouse=True)
def setup_aws(aws_credentials):
    """Mock all AWS calls for every test."""
    with mock_aws():
        yield

@pytest.fixture
def s3_bucket(setup_aws):
    """Creates a mock S3 bucket."""
    conn = boto3.client("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=os.environ["S3_BUCKET_NAME"])
    return conn

@pytest.fixture
def dynamodb_table(setup_aws):
    """Creates a mock DynamoDB table."""
    conn = boto3.resource("dynamodb", region_name="us-east-1")
    conn.create_table(
        TableName=os.environ["DYNAMODB_TABLE_NAME"],
        KeySchema=[{"AttributeName": "vehicle_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "vehicle_id", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    return conn

@pytest.fixture
def test_client(s3_bucket, dynamodb_table):
    """Returns a FastAPI TestClient."""
    return TestClient(app)
