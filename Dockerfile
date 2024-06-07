# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 7680

ADD start.sh /start.sh
RUN chmod +x /start.sh


# Run gunicorn when the container launches
CMD ["gunicorn", "--bind", ":7680", "beta.api.api:app"]