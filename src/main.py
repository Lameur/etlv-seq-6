"""
Main entry point for the Eco-Friendly Travel Analysis application.

This script imports the `run_analysis` function from the `app` package
and executes it when the script is run directly.
"""

import sys
import os

# Add the project root to the Python path to allow imports from 'app'
# Assumes this script is in the 'src' directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now we can import from the 'app' package located in 'src/app'
from app import run_analysis

if __name__ == "__main__":
    # Execute the main analysis function
    run_analysis()