#!/bin/bash
# Push to BareBones-Projects/alt-star-map-db

echo "Pushing to https://github.com/BareBones-Projects/alt-star-map-db"

# If repo already exists locally, pull first
# git clone https://github.com/BareBones-Projects/alt-star-map-db.git
# cd alt-star-map-db

git init
git add README.md .gitattributes .gitignore docs/ viewers/ data/ scripts/ .github/
git commit -m "🔒 LOCK ALL CODE - B&W Wireframe + Build DB B1-B6 (45k bodies 0-2500ly)"

git branch -M main
git remote add origin https://github.com/BareBones-Projects/alt-star-map-db.git

# Enable LFS
git lfs install
git lfs track "*.csv" "*.db" "*.png"

git push -u origin main

# For PR from feature branch:
# git checkout -b feature/bw-wireframe-lock-db-build
# git push -u origin feature/bw-wireframe-lock-db-build
# Then go to GitHub and click "Compare & pull request"

echo "Done! Now go to https://github.com/BareBones-Projects/alt-star-map-db"
echo "To create PR: git checkout -b feature/... && git push, then click PR button on GitHub"
