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

# Run setup script commands
RUN curl -o defaults.json https://raw.githubusercontent.com/shubhamakshit/pwdlv3/main/defaults.linux.json && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    if command -v python &> /dev/null; then \
        echo "Python is installed" && \
        if [[ $(uname -o) != "Android" ]]; then \
            python get-pip.py; \
        fi && \
        python -m pip install -r requirements.txt; \
    elif command -v python3 &> /dev/null; then \
        echo "Python3 is installed" && \
        if [[ $(uname -o) != "Android" ]]; then \
            python3 get-pip.py; \
        fi && \
        python3 -m pip install -r requirements.txt; \
    else \
        echo "Python is not installed" && \
        exit 1; \
    fi && \
    rm get-pip.py && \
    mkdir -p /app/bin && \
    curl -o /app/bin/mp4decrypt https://raw.githubusercontent.com/shubhamakshit/pwdlv3_assets/main/$(uname -o)/$(uname -m)/mp4decrypt && \
    curl -o /app/bin/vsd https://raw.githubusercontent.com/shubhamakshit/pwdlv3_assets/main/$(uname -o)/$(uname -m)/vsd && \
    chmod +x /app/bin/* && \
    if ! grep -q "alias pwdl" ~/.bashrc; then \
        echo "alias pwdl='python3 /app/pwdl.py'" >> ~/.bashrc; \
    fi && \
    echo "Please restart your terminal or run 'source ~/.bashrc' to apply the alias."

# Create webdl directory
RUN mkdir /app/webdl


