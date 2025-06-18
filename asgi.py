# asgi.py
from warehouse_stock_dashboard.main import app  # adjust import as needed

import os
import sys
from pathlib import Path

# Add your project directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent))

# 'app' is the FastAPI instance
application = app
