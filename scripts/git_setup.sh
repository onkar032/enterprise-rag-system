#!/bin/bash

# Git Setup Script for RAG System
# This script helps you set up and push your project to GitHub

echo "================================================"
echo "🚀 Git Setup for RAG System"
echo "================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    echo "   Visit: https://git-scm.com/downloads"
    exit 1
fi

echo "✓ Git is installed"
echo ""

# Check if already a git repository
if [ -d .git ]; then
    echo "⚠️  This is already a Git repository."
    echo ""
    read -p "Do you want to continue? This will show current status. (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 0
    fi
    git status
    exit 0
fi

# Initialize git
echo "Initializing Git repository..."
git init
echo "✓ Git repository initialized"
echo ""

# Configure git user (if not set)
if [ -z "$(git config user.name)" ]; then
    echo "Git user not configured."
    read -p "Enter your name: " git_name
    git config user.name "$git_name"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "Enter your email: " git_email
    git config user.email "$git_email"
fi

echo "✓ Git user configured"
echo "  Name: $(git config user.name)"
echo "  Email: $(git config user.email)"
echo ""

# Add all files
echo "Adding all files..."
git add .
echo "✓ All files added"
echo ""

# Show what will be committed
echo "Files to be committed:"
git status --short | head -20
total_files=$(git status --short | wc -l)
echo "... and $total_files files total"
echo ""

# Create first commit
echo "Creating first commit..."
git commit -m "feat: complete enterprise RAG system with production features

- Full RAG pipeline (ingestion, processing, retrieval, generation)
- Production features (API, UI, Docker, monitoring)
- Comprehensive documentation (README, Architecture, API docs)
- Advanced techniques (query rewriting, reranking, citations)
- Safety features (guardrails, PII detection)
- Evaluation framework (RAGAS + custom metrics)"

echo "✓ First commit created"
echo ""

# Rename branch to main
echo "Renaming branch to 'main'..."
git branch -M main
echo "✓ Branch renamed to 'main'"
echo ""

# Instructions for GitHub
echo "================================================"
echo "📝 Next Steps - Push to GitHub"
echo "================================================"
echo ""
echo "1. Go to GitHub.com and create a new repository:"
echo "   URL: https://github.com/new"
echo ""
echo "2. Repository details:"
echo "   Name: enterprise-rag-system"
echo "   Description: Production-grade RAG system with advanced AI techniques"
echo "   Visibility: Public (recommended for portfolio)"
echo "   ⚠️  DO NOT initialize with README, .gitignore, or license"
echo ""
echo "3. After creating the repository, run these commands:"
echo ""
echo "   # Replace YOUR_USERNAME with your GitHub username"
echo "   git remote add origin https://github.com/YOUR_USERNAME/enterprise-rag-system.git"
echo "   git push -u origin main"
echo ""
echo "================================================"
echo ""

read -p "Have you created the GitHub repository? (y/n): " created

if [ "$created" = "y" ]; then
    echo ""
    read -p "Enter your GitHub username: " github_user
    
    remote_url="https://github.com/$github_user/enterprise-rag-system.git"
    
    echo ""
    echo "Adding remote repository..."
    git remote add origin "$remote_url"
    echo "✓ Remote added: $remote_url"
    echo ""
    
    echo "Pushing to GitHub..."
    echo "⚠️  You may be asked for GitHub credentials"
    echo ""
    
    if git push -u origin main; then
        echo ""
        echo "================================================"
        echo "🎉 SUCCESS! Your project is now on GitHub!"
        echo "================================================"
        echo ""
        echo "🔗 Your repository: https://github.com/$github_user/enterprise-rag-system"
        echo ""
        echo "Next steps:"
        echo "1. Visit your repository and verify files uploaded"
        echo "2. Add a profile picture and description"
        echo "3. Add topics: ai, rag, llm, fastapi, machine-learning"
        echo "4. Consider adding screenshots to README"
        echo "5. Deploy to Streamlit Cloud for live demo"
        echo ""
    else
        echo ""
        echo "❌ Push failed. This might be due to:"
        echo "   - Invalid credentials"
        echo "   - Repository doesn't exist"
        echo "   - Network issues"
        echo ""
        echo "Try these steps:"
        echo "1. Verify repository exists: https://github.com/$github_user/enterprise-rag-system"
        echo "2. Check your GitHub credentials"
        echo "3. Try: git push -u origin main"
        echo ""
    fi
else
    echo ""
    echo "No problem! When ready, run:"
    echo ""
    echo "  git remote add origin https://github.com/YOUR_USERNAME/enterprise-rag-system.git"
    echo "  git push -u origin main"
    echo ""
fi

echo "================================================"
echo "📚 Useful Git Commands"
echo "================================================"
echo ""
echo "Check status:        git status"
echo "View history:        git log --oneline"
echo "View remote:         git remote -v"
echo "Add more changes:    git add ."
echo "Commit changes:      git commit -m 'your message'"
echo "Push changes:        git push"
echo ""
echo "For more help, see: https://docs.github.com/en/get-started"
echo ""

