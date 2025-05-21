from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_file_info(filename):
    """Get file information including size and modified date."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    stats = os.stat(file_path)
    size_kb = stats.st_size / 1024  # Convert to KB
    modified_date = datetime.fromtimestamp(stats.st_mtime)
    return {
        'name': filename,
        'size': f"{size_kb:.2f} KB",
        'modified': modified_date.strftime('%Y-%m-%d %H:%M:%S')
    }

@app.route('/')
def index():
    # Show upload form and list of files
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            files.append(get_file_info(filename))
    return render_template('index.html', files=files)

@app.route('/success', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('acknowledgement.html', name=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)