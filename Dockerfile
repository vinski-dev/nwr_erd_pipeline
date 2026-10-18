# 1. Use an official, lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the specific folders our dashboard needs to run
# This perfectly matches the paths we set up earlier!
COPY scripts/ scripts/
COPY sql/ sql/

# 5. Google Cloud Run expects web apps to listen on port 8080
EXPOSE 8080

# 6. Command to start the Streamlit app on the correct port
CMD ["streamlit", "run", "scripts/streamlit_health_dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]