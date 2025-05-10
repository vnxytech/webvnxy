import json
import csv
import io
import os
from werkzeug.utils import secure_filename

def parse_json(file_path):
    """Parse a JSON file and return its contents."""
    with open(file_path, 'r') as f:
        return json.load(f)

def parse_csv(file_path):
    """Parse a CSV file and return columns and rows."""
    columns = []
    rows = []
    
    with open(file_path, 'r', newline='') as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader):
            if i == 0:  # Header row
                columns = row
            else:
                rows.append(row)
    
    return columns, rows

def save_file(file, directory, filename=None):
    """Save an uploaded file to the specified directory."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    if not filename:
        filename = secure_filename(file.filename)
    
    file_path = os.path.join(directory, filename)
    file.save(file_path)
    
    return filename, file_path

def is_valid_file_type(filename, allowed_extensions=None):
    """Check if the file type is allowed."""
    if not allowed_extensions:
        allowed_extensions = ['.json', '.csv']
        
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in [ext.replace('.', '') for ext in allowed_extensions]

def get_file_extension(filename):
    """Get the file extension."""
    return os.path.splitext(filename)[1].lower()
