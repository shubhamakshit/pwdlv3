# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install -y ffmpeg

# Make port 5000 available to the world outside this container
EXPOSE 7680

RUN chmod +x ./setup.sh
RUN ./setup.sh

# Run gunicorn when the container launches
CMD ["gunicorn", "--bind", ":7680", "beta.api.api:app"]