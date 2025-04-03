# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pathlib import Path
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
os.environ["TORCH_WARN_ONCE_USE"] = "1"  # Reduces duplicate warnings

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
APP_DIR = Path(__file__).parent.parent.parent
CURRENT_DIR = None  # Placeholder for the current project directory

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
    global CURRENT_DIR  # Declare CURRENT_DIR as global
    try:
        # Parse the JSON data from the request
        data = request.get_json()
        content = data.get('content', [])
        filename = data.get('filename', "")
        project_dir = create_projectfolder(filename)
        processed_sections = [section.strip() for section in content if section.strip()]
        save_sections(processed_sections, project_dir)
        CURRENT_DIR = project_dir  # Update the global current directory
        # Respond with a success message
        return jsonify({"message": "File uploaded and processed successfully!", "sections": processed_sections})
    except Exception as e:
        print("Error processing file:", str(e))
        return jsonify({"message": "Error processing file!", "error": str(e)}), 500

# handle cinversion to latex with AI
@app.route('/api/parse', methods=['GET'])
def convert_txt_to_latex():
    try:
        INPUT_DIR = os.path.join(CURRENT_DIR, "sections")
        OUTPUT_DIR = os.path.join(CURRENT_DIR, "latex_output")
        tokenizer, model = setup_model("google/flan-t5-large")
        print(f"Working in current Directory: {CURRENT_DIR}")  # log

        # Read the prompt from the prompt.txt file
        prompt_file = os.path.join(APP_DIR, "prompt.txt")
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt file not found at: {prompt_file}")
        else:
            with open(prompt_file, "r") as file:
                prompt = file.read()

        # create output folder
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)  # Create the directory
            print(f"Directory created at: {OUTPUT_DIR}")  # log
        else:
            print(f"Directory already exists: {OUTPUT_DIR}")
        
        # Process each section in the input directory
        sections = os.listdir(INPUT_DIR)
        for section_file in sections:
            section_path = os.path.join(INPUT_DIR, section_file)
            if os.path.isfile(section_path):
                with open(section_path, "r") as file:
                    section_content = file.read()
            else: 
                print(f"No file with found under {section_path}")
                continue

            # Generate the output using the model
            input_text = prompt.replace("{content}", section_content)

            inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).to("cuda")
            with torch.no_grad():  # Reduces memory usage
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    num_beams=4,
                    temperature=0.3,
                    early_stopping=True  # Helps prevent runaway generation
                )
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            print(f"Generated text for {section_file}: {generated_text}")  # log

            # Save the generated output to the output directory
            output_file = os.path.join(OUTPUT_DIR, f"parsed_{section_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(generated_text)

            print(f"Processed and saved: {output_file}")     
        return jsonify({"message": "File processed and parsed with AI successfully!"})
    except Exception as e:
        print("Error parsing file with AI:", str(e))
        return jsonify({"message": "Error parsing file with AI!", "error": str(e)}), 500

def setup_model(name):
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        name,
        torch_dtype=torch.float16,  # FP16 for VRAM efficiency
        device_map="auto"
    )
    return tokenizer, model

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