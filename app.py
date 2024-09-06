from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os

from dotenv import load_dotenv
from typing import Set
from backend.core_2 import run_llm

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}. {source}\n"
    return sources_string

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_prompt = request.json.get('prompt')
    
    if user_prompt:
        generated_response = run_llm(query=user_prompt, chat_history=request.json.get('chat_history', []))
        sources = set(doc.metadata["source"] for doc in generated_response["context"])
        formatted_response = f"{generated_response['answer']} \n\n {create_sources_string(sources)}"
        return jsonify({"response": formatted_response})
    
    return jsonify({"response": "No prompt provided"}), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return jsonify({"response": "No file part"}), 400
    
    file = request.files['document']
    if file.filename == '':
        return jsonify({"response": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({"response": f"File {filename} uploaded successfully"})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
