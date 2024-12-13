import os
import shutil
from flask import Flask, request, jsonify, send_from_directory, send_file
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'images' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('images')
    for file in files:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))

    # Run normal_map.py and wait for it to finish
    subprocess.run(['python', '../normal_map.py', '-i', UPLOAD_FOLDER, '-o', 'temp/normal_map.png'], check=True)

    # Send intermediate response to indicate normal map is ready
    return jsonify({
        'normalMapUrl': '/temp/normal_map.png',
        'status': 'normal_map_ready'
    })

@app.route('/process_normals', methods=['POST'])
def process_normals():
    # Run 3d_from_normals.py after normal_map.py finishes
    subprocess.run(['python', '../3d_from_normals.py', '-i', 'temp/normal_map.png', '-o', 'temp/output.obj'], check=True)

    return jsonify({
        'objUrl': '/temp/output.obj',
        'status': 'obj_ready'
    })

@app.route('/temp/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)