FROM python:3.9

WORKDIR /app

# Install dependencies for Node.js
RUN apt-get update && apt-get install -y ca-certificates curl gnupg

# Create keyrings directory
RUN mkdir -p /etc/apt/keyrings

# Add NodeSource GPG key
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

# Set Node.js version and add repository
ENV NODE_MAJOR=20
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" > /etc/apt/sources.list.d/nodesource.list

# Update package lists and install Node.js
RUN apt-get update && apt-get install -y nodejs

# Verify installations
RUN python --version && node --version && npm --version

# Copy the current directory contents into the container
COPY . .

# Install any required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script
CMD ["python", "script.py"]