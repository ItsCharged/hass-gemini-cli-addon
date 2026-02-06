#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: Gemini CLI Agent
# This script starts the Flask web server for the Gemini CLI agent.
# ==============================================================================

# Ensure the working directory is /app
cd /app

# Execute the Flask app.py
# Using exec ensures that signals are properly handled and the Flask app
# becomes the main process of the container.
exec python3 app.py