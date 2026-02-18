"""
Simple Flask web app for exploring data analysis results
"""

from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
import os
from datetime import datetime
import subprocess
import sys

app = Flask(__name__, template_folder='templates', static_folder='static')

# Directories
DATA_DIR = 'data'
RESULTS_DIR = 'results'
VIZ_DIR = 'notebooks/visualizations'

# Helper functions

def check_if_data_exists():
    """Check what analysis files we have"""
    return {
        'raw_data': os.path.exists(os.path.join(DATA_DIR, 'OnlineRetail.csv')),
        'cleaned_data': os.path.exists(os.path.join(RESULTS_DIR, 'cleaned_data.csv')),
        'visualizations': os.path.exists(VIZ_DIR) and len(os.listdir(VIZ_DIR)) > 0
    }

def load_data_preview(filepath, rows=5):
    """Load first few rows of CSV"""
    try:
        df = pd.read_csv(filepath)
        return {
            'rows': len(df),
            'columns': df.columns.tolist(),
            'preview': df.head(rows).values.tolist()
        }
    except Exception as e:
        return {'error': str(e)}

# Routes

@app.route('/')
def home():
    """Home page - shows project info and status"""
    status = check_if_data_exists()
    return render_template('index.html', status=status)

@app.route('/dashboard')
def dashboard():
    """Dashboard - view all results and visualizations"""
    status = check_if_data_exists()
    
    # get list of chart images
    viz_files = []
    if os.path.exists(VIZ_DIR):
        viz_files = [f for f in os.listdir(VIZ_DIR) if f.endswith('.png')]
    
    return render_template('dashboard.html', status=status, viz_files=sorted(viz_files))

@app.route('/viz/<filename>')
def get_viz(filename):
    """Serve visualization images"""
    return send_file(os.path.join(VIZ_DIR, filename), mimetype='image/png')

@app.route('/api/status')
def api_status():
    """Check what files exist"""
    return jsonify(check_if_data_exists())

@app.route('/api/data-preview')
def api_data_preview():
    """Preview raw data"""
    filepath = os.path.join(DATA_DIR, 'OnlineRetail.csv')
    if os.path.exists(filepath):
        return jsonify(load_data_preview(filepath, rows=10))
    return jsonify({'error': 'Data not found'})

@app.route('/api/cleaned-data')
def api_cleaned_data():
    """Preview cleaned data"""
    filepath = os.path.join(RESULTS_DIR, 'cleaned_data.csv')
    if os.path.exists(filepath):
        return jsonify(load_data_preview(filepath, rows=10))
    return jsonify({'error': 'Cleaned data not found'})

@app.route('/api/run-analysis', methods=['POST'])
def api_run_analysis():
    """Run analysis scripts and return status"""
    try:
        # Run data cleaning
        result = subprocess.run(
            [sys.executable, 'src/01_data_cleaning.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            return jsonify({'error': f'Cleaning failed: {result.stderr}'}), 400
        
        # Run exploratory analysis
        result = subprocess.run(
            [sys.executable, 'src/02_exploratory_analysis.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            return jsonify({'error': f'Analysis failed: {result.stderr}'}), 400
        
        # Run statistical analysis
        result = subprocess.run(
            [sys.executable, 'src/03_statistical_analysis.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            return jsonify({'error': f'Stats failed: {result.stderr}'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Analysis complete',
            'timestamp': datetime.now().isoformat()
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Analysis took too long (timeout)'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filetype>')
def download(filetype):
    """Download CSV results"""
    try:
        if filetype == 'cleaned':
            filepath = os.path.join(RESULTS_DIR, 'cleaned_data.csv')
            return send_file(filepath, as_attachment=True, download_name='cleaned_data.csv')
        elif filetype == 'report':
            filepath = os.path.join(RESULTS_DIR, 'cleaning_report.csv')
            return send_file(filepath, as_attachment=True, download_name='cleaning_report.csv')
        return jsonify({'error': 'Unknown file type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error pages

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Main

if __name__ == '__main__':
    # Create folders if they don't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(VIZ_DIR, exist_ok=True)
    
    print("\nFlask app starting...")
    print("Open http://localhost:5000 in your browser\n")
    
    app.run(debug=True, host='localhost', port=5000)
    if __name__ == "__main__":
        app.run()
