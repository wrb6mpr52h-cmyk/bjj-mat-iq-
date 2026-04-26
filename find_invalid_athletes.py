import os
import json

# Directories to check (add more if needed)
athlete_dirs = [
    'athletes',
    os.path.join('data', 'athletes'),
    os.path.join('data', 'users')
]

def find_invalid_athlete_files():
    invalid_files = []
    for base_dir in athlete_dirs:
        if not os.path.exists(base_dir):
            continue
        if base_dir.endswith('users'):
            # Check all user subfolders
            for user in os.listdir(base_dir):
                user_athlete_dir = os.path.join(base_dir, user, 'athletes')
                if os.path.exists(user_athlete_dir):
                    invalid_files.extend(check_dir(user_athlete_dir))
        else:
            invalid_files.extend(check_dir(base_dir))
    return invalid_files

def check_dir(directory):
    files = []
    for fname in os.listdir(directory):
        if fname.endswith('.json'):
            fpath = os.path.join(directory, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'name' not in data or not data['name']:
                    files.append(fpath)
            except Exception as e:
                files.append(fpath)
    return files

if __name__ == '__main__':
    invalids = find_invalid_athlete_files()
    if invalids:
        print('Invalid athlete files (missing or empty name):')
        for f in invalids:
            print(f)
    else:
        print('All athlete files have valid names.')
