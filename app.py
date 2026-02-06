import subprocess
import os
import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

GEMINI_CLI_COMMAND = "gemini"
DEFAULT_MODEL = "gemini-2.5-flash-image"
APPROVAL_MODE = "yolo" # User selected "yolo"

chat_sessions = {}

def get_session_id():
    return request.remote_addr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    session_id = get_session_id()
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    chat_sessions[session_id].append({"role": "user", "content": user_message})

    full_prompt = "
".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_sessions[session_id]])

    try:
        command = [
            GEMINI_CLI_COMMAND,
            "-m", DEFAULT_MODEL,
            "-p", full_prompt,
            "-o", "json",
            "--approval-mode", APPROVAL_MODE
        ]
        
        app.logger.info(f"Executing Gemini CLI command: {' '.join(command)}")

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode != 0:
            app.logger.error(f"Gemini CLI process exited with error code {process.returncode}: {process.stderr}")
            try:
                error_output = json.loads(process.stderr)
                gemini_response_content = error_output.get("error", {}).get("message", "Unknown Gemini CLI error")
            except json.JSONDecodeError:
                gemini_response_content = process.stderr.strip()
            
            chat_sessions[session_id].append({"role": "gemini", "content": f"Error: {gemini_response_content}"})
            return jsonify({"response": f"Error: {gemini_response_content}"}), 500

        gemini_raw_output = process.stdout.strip()
        
        try:
            gemini_json_output = json.loads(gemini_raw_output)
            gemini_response_content = gemini_json_output.get("text", gemini_raw_output)
        except json.JSONDecodeError:
            app.logger.error(f"Failed to decode JSON from Gemini CLI output: {gemini_raw_output}")
            gemini_response_content = gemini_raw_output

        chat_sessions[session_id].append({"role": "gemini", "content": gemini_response_content})
        
        return jsonify({"response": gemini_response_content})

    except FileNotFoundError:
        app.logger.error(f"Gemini CLI command '{GEMINI_CLI_COMMAND}' not found. Please ensure it's installed and in PATH.")
        gemini_response_content = f"Error: Gemini CLI command '{GEMINI_CLI_COMMAND}' not found. Please ensure it's installed and in PATH."
        chat_sessions[session_id].append({"role": "gemini", "content": gemini_response_content})
        return jsonify({"error": gemini_response_content}), 500
    except Exception as e:
        app.logger.error(f"Internal server error: {e}")
        gemini_response_content = "Internal server error."
        chat_sessions[session_id].append({"role": "gemini", "content": gemini_response_content})
        return jsonify({"error": gemini_response_content}), 500

@app.route('/restart', methods=['POST'])
def restart():
    session_id = get_session_id()
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return jsonify({"status": "Gemini CLI session (frontend context) restarted."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
