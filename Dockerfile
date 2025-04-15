# syntax=docker/dockerfile:1.4
FROM python:3.12
LABEL authors="gouzu"

# Set the working directory
WORKDIR /app

# Copy project code
COPY /QQBotAPI /app/QQBotAPI
COPY /src /app/src
COPY /src /app
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
# 缓存 pip 依赖
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Expose port
EXPOSE 8000

# Create and expose directories
VOLUME ["/app/databases", "/app/apps", "/app/AppData","/app/logs"]

# Run the application
ENV PYTHONPATH=/app
WORKDIR /app/src
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]