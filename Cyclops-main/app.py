from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Import CORS
from brain import *
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Rest of the code...

# Initialize the assistant
if os.path.exists("user_pref.txt"):
    with open('user_pref.txt', 'r') as f:
        user_name = f.readline().strip().split(": ")[1]
else:
    user_name = "User"  # Default name if no preferences are found

message, llama_model = llama_message_init(USER_DETAILS)

# Home route
@app.route('/')
def home():
    return render_template('index.html', username=user_name)

# API endpoint to process commands
@app.route('/command', methods=['POST'])
def command():
    data = request.json
    command = data.get('command', '').strip()

    if not command:
        return jsonify({'response': 'No command provided'})

    # Process the command using the existing brain.py functions
    response, function, message = LLM_answer(command, message, llama_model)

    # Execute any associated function (e.g., play music, set timer, etc.)
    if function:
        llm_interpreter(function, response)

    return jsonify({'response': response})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False)  # Disable debug mode to avoid Windows error 6