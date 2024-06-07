# Use an official Ubuntu runtime as a parent image
FROM ubuntu:latest

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install Python, pip and ffmpeg
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg

# Install any needed packages specified in requirements.txt
RUN python3 -m pip3 install --no-cache-dir -r requirements.txt

# Make port 7680 available to the world outside this container
EXPOSE 7680

RUN chmod +x ./setup.sh
RUN ./setup.sh

# Run gunicorn when the container launches
CMD ["gunicorn", "--bind", ":7680", "beta.api.api:app"]