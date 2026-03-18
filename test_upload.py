#!/usr/bin/env python
"""Test image upload functionality"""
import requests
from PIL import Image
import io
import sys

# Create a simple test image (solid green)
img = Image.new('RGB', (224, 224), color='green')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_byte_arr.seek(0)

# Test the API
print("Testing /api/predict endpoint...")
try:
    files = {'file': ('test.png', img_byte_arr, 'image/png')}
    response = requests.post('http://127.0.0.1:5000/api/predict', files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
