#!/usr/bin/env python3
import os
import aws_cdk as cdk
from infrastructure.infrastructure_stack import AutoInsightStack

app = cdk.App()
AutoInsightStack(app, "AutoInsightStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION', 'us-east-1')
    ),
)

app.synth()
