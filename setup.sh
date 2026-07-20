#!/bin/bash
set -e
echo "🚀 Setting up GitHub Pages and remote..."
git checkout --orphan gh-pages 2>/dev/null || git checkout gh-pages
git rm -rf .
git commit --allow-empty -m "Initial gh-pages"
git push origin gh-pages
git checkout main 2>/dev/null || git checkout master
echo "✅ gh-pages branch created."
echo ""
echo "🌐 To deploy the backend to a cloud service:"
echo "   1. Set up a container registry (e.g., Docker Hub, ghcr.io)"
echo "   2. Update .github/workflows/deploy.yml (set 'if: true' and add secrets)"
echo "   3. Or manually: docker build -t your-image ./backend && docker push ..."
echo "   4. Deploy to Render/Fly.io/your provider with the built image."
echo ""
echo "📌 Your frontend will be available at:"
echo "   https://swipswaps.github.io/$REPO_NAME/"
echo ""
echo "To start backend locally:"
echo "   docker-compose up --build"
