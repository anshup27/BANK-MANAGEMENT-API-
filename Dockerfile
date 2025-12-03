# Use lightweight python image
FROM python:3.10-slim

# Set working directory
WORKDIR /api-flask

# Install system dependencies (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy folder assets
COPY static/ /api-flask/static/
COPY util/ /api-flask/util/

# Copy configuration files
COPY .env /api-flask/.env
COPY swaggerConfig.py /api-flask/swaggerConfig.py
COPY config.json /api-flask/config.json
COPY .gitignore /api-flask/.gitignore

# Copy app files
COPY application.py /api-flask/application.py
COPY auth.py /api-flask/auth.py
COPY bankResource.py /api-flask/bankResource.py

# Copy DB files (if you want DB inside container)
COPY bank.db /api-flask/bank.db
COPY bank_new.db /api-flask/bank_new.db

# Copy test files (if you need them)
COPY test_account_api.py /api-flask/test_account_api.py

# Copy requirements file
COPY requirements.txt /api-flask/requirements.txt

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "application.py"]
