"""
Launcher script for Streamlit app
Run: python run_app.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variable for streamlit
os.environ['PYTHONPATH'] = str(project_root)

# Run streamlit
import subprocess
subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'frontend/streamlit_app.py'])
