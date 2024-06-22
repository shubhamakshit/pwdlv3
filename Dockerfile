# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install ffmpeg and curl
RUN apt-get update && apt-get install -y ffmpeg curl

# Create a virtual environment and activate it
RUN python -m venv /opt/venv

# Ensure the virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 7680 available to the world outside this container
EXPOSE 7680

# Copy defaults.json from the given URL
COPY ./defaults.linux.json ./defaults.json

# Add setup.sh script
COPY setup.sh ./setup.sh

# Run setup.sh script
RUN chmod +x ./setup.sh && ./setup.sh

# Ensure bin directory scripts are executable
RUN chmod +x ./bin/*

# Create webdl directory
RUN mkdir webdl

# Run gunicorn when the container launches
CMD ["gunicorn", "--workers", "8", "--bind", "0.0.0.0:7680", "app:app"]
