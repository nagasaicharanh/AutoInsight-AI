from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_iam as iam,
)
from constructs import Construct
import os

class AutoInsightStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. S3 Bucket for raw telemetry
        bucket = s3.Bucket(
            self, "TelemetryBucket",
            bucket_name="autoinsight-telemetry",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
        )

        # 2. DynamoDB Table for summaries
        table = dynamodb.Table(
            self, "SummariesTable",
            table_name="autoinsight-summaries",
            partition_key=dynamodb.Attribute(
                name="vehicle_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # 3. Docker Lambda Function
        # We assume the Dockerfile is in the project root
        lambda_fn = _lambda.DockerImageFunction(
            self, "AutoInsightHandler",
            code=_lambda.DockerImageCode.from_image_asset(
                directory=".", # Project root context
                file="Dockerfile"
            ),
            memory_size=512,
            timeout=_lambda.Duration.seconds(30),
            environment={
                "S3_BUCKET_NAME": bucket.bucket_name,
                "DYNAMODB_TABLE_NAME": table.table_name,
                "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", ""),
            }
        )

        # 4. IAM Permissions
        bucket.grant_read_write(lambda_fn)
        table.grant_read_write_data(lambda_fn)

        # 5. API Gateway HTTP API
        http_api = apigwv2.HttpApi(
            self, "AutoInsightApi",
            api_name="AutoInsight API",
        )

        # 6. API Routes
        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            handler=lambda_fn
        )

        http_api.add_routes(
            path="/ingest",
            methods=[apigwv2.HttpMethod.POST],
            integration=lambda_integration
        )

        http_api.add_routes(
            path="/summary/{vehicle_id}",
            methods=[apigwv2.HttpMethod.GET],
            integration=lambda_integration
        )
        
        http_api.add_routes(
            path="/health",
            methods=[apigwv2.HttpMethod.GET],
            integration=lambda_integration
        )

        # 7. Outputs
        CfnOutput(
            self, "ApiUrl",
            value=http_api.api_endpoint,
            description="The URL of the API Gateway"
        )
