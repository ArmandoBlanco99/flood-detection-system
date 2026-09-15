#!/usr/bin/env python
"""Script for running the application in production mode.
Requires Gunicorn: pip install gunicorn"""

import os
import sys
from pathlib import Path

# Add the src directory to the import path
src_dir = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_dir))

from src.flask_server import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
