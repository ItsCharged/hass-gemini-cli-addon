# Use a Node.js image as base, which includes npm
FROM node:20-slim

# Install Python and pip (for Flask)
RUN apt-get update && 
    apt-get install -y --no-install-recommends python3 python3-pip && 
    apt-get clean && 
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Flask and other Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Gemini CLI globally
# The command for installing gemini CLI might vary. 
# From `package.json` results, it's `@google/gemini-cli`.
# Assuming `npm i -g @google/gemini-cli` is the way.
RUN npm install -g @google/gemini-cli

# Copy the application code
COPY app.py .
COPY templates/ templates/

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the application
# Ensure 'gemini' executable is in the PATH for subprocess.
# /usr/local/bin is typically in the PATH for Node.js images, but explicitly adding for clarity.
ENV PATH="/usr/local/bin:${PATH}" 

CMD ["python3", "app.py"]