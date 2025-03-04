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
RUN pip3 install --no-cache-dir -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Expose port
EXPOSE 8000

# Create and expose directories
RUN mkdir -p /app/databases /app/apps /app/AppData
VOLUME ["/app/databases", "/app/apps", "/app/AppData","/app/logs"]

# Run the application
ENV PYTHONPATH=/app
WORKDIR /app/src
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]