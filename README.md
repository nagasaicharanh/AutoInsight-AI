# AutoInsight-AWS

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![AWS CDK](https://img.shields.io/badge/AWS%20CDK-v2-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.100+-green.svg)

AutoInsight-AWS is a serverless AI-powered vehicle telemetry analysis platform. It ingests telemetry data, stores it securely on AWS, and utilizes Groq's LLM (Llama 3) to provide real-time diagnostic summaries and severity assessments.

## Architecture

```mermaid
graph TD
    A[Vehicle / Client] -->|POST /ingest| B(API Gateway)
    B --> C[Lambda - FastAPI]
    C -->|Store Raw| D[(S3 Bucket)]
    C -->|Store Metadata| E[(DynamoDB Table)]
    C -->|Analyze| F[Groq AI - Llama 3]
    F -->|Return Summary| C
    C -->|Save Summary| E
    G[Dashboard / User] -->|GET /summary/{id}| B
```

## Tech Stack

- **Backend:** FastAPI, Mangum (Lambda adapter)
- **AI:** Groq SDK (Llama-3.3-70b-versatile)
- **Infrastructure:** AWS CDK (Python)
- **Storage:** AWS S3 (Raw JSON), AWS DynamoDB (Metadata & Summaries)
- **Testing:** Pytest, Moto (Mock AWS), Pytest-cov
- **CI/CD:** GitHub Actions

## Features

- **Serverless Ingestion:** Highly scalable ingestion endpoint via AWS Lambda and API Gateway.
- **AI Diagnostics:** Automated severity assessment and summary generation using state-of-the-art LLMs.
- **Secure Storage:** Raw data versioning and encryption in S3; structured metadata in DynamoDB.
- **Infrastructure as Code:** Fully automated provisioning via AWS CDK.
- **Automated Testing:** 80%+ test coverage with mocked AWS and AI services.

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/AutoInsight-AI.git
   cd AutoInsight-AI
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest-asyncio
   ```

4. **Set environment variables:**
   ```bash
   export GROQ_API_KEY=your_api_key
   export AWS_REGION=us-east-1
   ```

5. **Run tests:**
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   pytest tests/ -v --cov=app
   ```

## Deployment to AWS

1. **Configure AWS CLI:**
   ```bash
   aws configure
   ```

2. **Install CDK CLI:**
   ```bash
   npm install -g aws-cdk
   ```

3. **Deploy the stack:**
   ```bash
   cd infrastructure
   pip install -r requirements.txt
   cdk bootstrap
   cdk deploy
   ```

## License
MIT
