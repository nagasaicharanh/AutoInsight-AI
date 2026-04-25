FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN pip install -r requirements.txt

# Copy app code
COPY app/ ${LAMBDA_TASK_ROOT}/app/

# Set the CMD to your handler (Mangum handler in main.py)
CMD [ "app.main.handler" ]
