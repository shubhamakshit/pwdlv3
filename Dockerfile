# Use an official Python runtime as a parent image
FROM python:3.12-slim as build
# Set the working directory in the container to /app
WORKDIR /app
# Add the current directory contents into the container at /app
COPY . /app
# Install ffmpeg, curl, and other necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*
# Create a virtual environment and activate it
RUN python -m venv /opt/venv
# Ensure the virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Copy defaults.json from the given URL
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

# Use a minimal image for the runtime
FROM python:3.12-slim
# Set the working directory in the container to /app
WORKDIR /app
# Install ffmpeg in the final image
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
# Copy only the necessary files from the build stage
COPY --from=build /opt/venv /opt/venv
COPY --from=build /app /app
# Ensure the virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"
# Add /app/bin to PATH to ensure executables are available
ENV PATH="/app/bin:$PATH"
# Set Flask environment variables
ENV FLASK_DEBUG=1
ENV FLASK_ENV=development
ENV FLASK_APP=run:app
# Make port 5000 available to the world outside this container
EXPOSE 5000
# Create a wrapper script that verifies ffmpeg and runs pwdl.py before flask
RUN echo '#!/bin/bash\n\n# Verify ffmpeg installation\necho "Testing ffmpeg installation:"\nffmpeg -version\n\n# Run pwdl.py in verbose mode\necho "Starting pwdl.py in verbose mode..."\npython3 /app/pwdl.py --verbose\n\n# Start Flask application\necho "Starting Flask application..."\nexec flask run --host=0.0.0.0' > /app/start.sh && \
    chmod +x /app/start.sh
# Run the wrapper script
ENTRYPOINT ["/app/start.sh"]