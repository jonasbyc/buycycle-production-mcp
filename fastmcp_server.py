#!/usr/bin/env python3
"""
Entry point for running the Buycycle Listing MCP Server on FastMCP.
This file points to the ASGI app in the HTTP server wrapper.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the ASGI app object from the HTTP server
from buycycle_http_server import app

# The 'app' object is now the ASGI application that FastMCP will run.