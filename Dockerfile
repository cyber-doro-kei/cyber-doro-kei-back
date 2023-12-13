# backend/Dockerfile
FROM python:3.11

WORKDIR /backend

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the timezone to JST (Japan Standard Time)
ENV TZ Asia/Tokyo

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--reload"]

