from time import sleep
from flask import Flask, request, jsonify
import os
from flask_cors import CORS, cross_origin


from gpt import get_gpt_results
from text_extraction import extract_interview_notes, extract_job_description, extract_resume_info

app = Flask(__name__)

CORS(app)

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/hello', methods=["GET"])
def hello_world():
    return jsonify({'message': 'hello, world!'}), 200

@app.route('/upload', methods=['POST'])
def upload_files():
    required_files = ['job_description', 'resume', 'interview_notes']
    missing_files = [file for file in required_files if file not in request.files]
    
    if missing_files:
        return jsonify({'error': f'Missing files: {", ".join(missing_files)}'}), 400

    saved_files = {}
    for file_key in required_files:
        file = request.files[file_key]
        if file.filename == '':
            return jsonify({'error': f'File for {file_key} is empty.'}), 400
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': f'{file_key} must be a PDF file.'}), 400

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        saved_files[file_key] = file_path

    strengths, areas_of_improvement, job_fit = extract_interview_notes(saved_files["interview_notes"])
    requirements, responsibilities = extract_job_description(saved_files["job_description"]) 
    resume_info = extract_resume_info(saved_files["resume"])
    """
    return jsonify({
        "satisfied_requirements": "b",
        "unsatisfied_requirements": "c",
        "interview_fit": "d",
        "strengths": "e",
        "areas_of_improvement": "f",
        "overall_conclusion": "g",
        "strengths_count": "1",
        "areas_of_improvement_count": "2",
        "satisfied_requirements_count": "3",
        "unsatisfied_requirements_count": "4"

    }), 200
    """
    gpt_results = get_gpt_results(resume_info, (strengths, areas_of_improvement, job_fit), requirements, responsibilities)
    return jsonify(gpt_results), 200

if __name__ == '__main__':
    app.run(debug=True)

