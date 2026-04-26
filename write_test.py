import os
import json

# Directory and file path
athlete_dir = os.path.join('data', 'users', 'MSantone', 'athletes')
os.makedirs(athlete_dir, exist_ok=True)
file_path = os.path.join(athlete_dir, 'write_test.json')

data = {'test': 'This is a test file.'}

try:
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[SUCCESS] File written to: {file_path}")
except Exception as e:
    print(f"[ERROR] Could not write file: {e}")
