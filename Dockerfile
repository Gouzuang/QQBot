FROM python:3.12
LABEL authors="gouzu"

# Set the working directory
WORKDIR /app

# Copy project code
COPY /QQBotAPI /app/QQBotAPI
COPY /shared /app/shared
COPY /src /app
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Expose port
EXPOSE 8000

# Create and expose directories
RUN mkdir -p /databases /apps /AppData
VOLUME ["/databases", "/apps", "/AppData"]

# Run the application
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]