#!/usr/bin/env python
"""Local server entry point.

Runs the app with Flask's built-in server via `python wsgi.py` — this
is a local/demo server, not a production WSGI server. For genuine
production deployment, serve this module's `app` object with a real
WSGI server instead, e.g.:
    pip install gunicorn
    gunicorn wsgi:app
"""

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
