#!/usr/bin/env python3
"""Quick test to verify the Flask app works locally before deployment"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("Testing local Flask app...")
    print("Visit: http://localhost:5000")
    print("Array tool: http://localhost:5000/array-tool.html")
    app.run(debug=True, port=5000)