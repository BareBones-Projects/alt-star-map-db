# Fix large file error

GitHub limit 100MB. Your cumulative CSV ~15MB should be OK with LFS, but best is Releases.

To push:
git lfs install
git lfs track "*.csv" "*.db"
git add .
git commit -m "Lock B&W wireframe + B1-B6 45k bodies"
git push

If fails, push lite:
git add README.md .gitattributes .gitignore docs/ viewers/ data/sample*.csv
git commit -m "Lite - will commit"
git push

Then upload large files via Releases page on GitHub.
