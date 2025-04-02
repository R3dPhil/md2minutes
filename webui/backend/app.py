# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pathlib import Path
import os

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
APP_DIR = Path(__file__).parent.parent.parent

# Create a Flask app instance
app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR / "static"),
    static_url_path="/static",
    template_folder=str(FRONTEND_DIR)
) 
CORS(app)

# rrender the index.html file from the frontend directory
@app.route('/')
def serve_index():
    return render_template('index.html')

# Serve the static files from the frontend directory
@app.route('/api/data')
def get_data():
    return jsonify({"message": "Backend is running!"})

# handle file upload and processing
@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        # Parse the JSON data from the request
        data = request.get_json()
        content = data.get('content', [])
        filename = data.get('filename', "")
        project_dir = create_projectfolder(filename)
        processed_sections = [section.strip() for section in content if section.strip()]
        save_sections(processed_sections, project_dir)
        # Respond with a success message
        return jsonify({"message": "File uploaded and processed successfully!", "sections": processed_sections})
    except Exception as e:
        print("Error processing file:", str(e))
        return jsonify({"message": "Error processing file!", "error": str(e)}), 500

# handle cinversion to latex with AI
@app.route('/api/parse', methods=['GET'])
def parse_files():
    try:
        # AI Parsing Logic
        from transformers import pipeline

        # Load a pre-trained model for text summarization or parsing
        # summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        # Use the AI model to parse or summarize the sections
        # ai_parsed_sections = [summarizer(section, max_length=50, min_length=10, do_sample=False)[0]['summary_text'] for section in processed_sections]

        # Respond with the AI-parsed sections
        return jsonify({"message": "File processed and parsed with AI successfully!"})
    except Exception as e:
        print("Error parsing file with AI:", str(e))
        return jsonify({"message": "Error parsing file with AI!", "error": str(e)}), 500

# create project directory
def create_projectfolder(filename, iteration=0):
    # Create a directory for the project if it doesn't exist
    if iteration != 0:
        project_dir = os.path.join(APP_DIR, "projects", filename + "_" + str(iteration))
    else:
        project_dir = os.path.join(APP_DIR, "projects", filename)
    if iteration == 100:  # Prevent infinite recursion
        print("Max iterations (100) of the same file reached. Exiting...")
        return project_dir
    
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)  # Create the directory
        print(f"Directory created at: {project_dir}")  # log
        return project_dir
    else:
        # Recursive call with incremented iteration
        print(f"Project with the name <<{filename}> >already exists.")  # log
        return create_projectfolder(filename, iteration + 1)

# save the sections to a directory
def save_sections(sections, project_dir):
    # dir exists check
    save_sections_dir = os.path.join(project_dir, "sections")
    if os.path.exists(save_sections_dir):
        os.rmdir(save_sections_dir)
    else:
        print(f"Directory created: {save_sections_dir}") # log
    os.makedirs(save_sections_dir) # Create directory

    for i, section in enumerate(sections, start=0):  # Enumerate to create unique filenames
        file_path = os.path.join(save_sections_dir, f'section_{i}.txt')  # Create a unique file for each section
        with open(file_path, "w") as file:
            file.write(section)

    print(f"Sections saved to: {save_sections_dir}") # log

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000)