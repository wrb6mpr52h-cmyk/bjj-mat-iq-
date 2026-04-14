# BJJ Mat IQ - GitHub Setup Commands

## 1. Initialize Git Repository (run in your project folder)
git init

## 2. Add all necessary files
git add app.py
git add athlete_manager.py
git add config.py
git add review_engine.py  
git add user_manager.py
git add requirements.txt
git add .streamlit/config.toml
git add logo.png
git add README.md
git add .gitignore

## 3. Create initial data structure folders (empty folders for cloud)
mkdir -p data/athletes
mkdir -p data/reviews  
mkdir -p data/users/Administrator/athletes
mkdir -p data/users/Administrator/reviews

# Add empty .gitkeep files to preserve folder structure
touch data/athletes/.gitkeep
touch data/reviews/.gitkeep
touch data/users/Administrator/athletes/.gitkeep
touch data/users/Administrator/reviews/.gitkeep

git add data/athletes/.gitkeep
git add data/reviews/.gitkeep
git add data/users/Administrator/athletes/.gitkeep
git add data/users/Administrator/reviews/.gitkeep

## 4. Make initial commit
git commit -m "Initial commit: BJJ Mat IQ application"

## 5. Connect to GitHub (replace with your repository URL)
git remote add origin https://github.com/yourusername/bjj-mat-iq.git
git branch -M main
git push -u origin main

## 6. For updates after changes
git add .
git commit -m "Description of changes"
git push