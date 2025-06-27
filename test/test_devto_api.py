#!/usr/bin/env python3
"""
Simple script to test Dev.to API functionality
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from test.devto_api_test import main

if __name__ == "__main__":
    print("🔍 Dev.to API Test")
    print("=" * 50)
    main() 