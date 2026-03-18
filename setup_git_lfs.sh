#!/bin/bash
# Git LFS Setup Script
# This script configures Git LFS for tracking large model files

set -e  # Exit on any error

echo "🔧 Git LFS Setup Script"
echo "======================="
echo ""

# Step 1: Check if Git LFS is installed
echo "📦 Checking Git LFS installation..."
if ! command -v git-lfs &> /dev/null; then
    echo "❌ Git LFS is not installed."
    echo ""
    echo "📥 Install Git LFS:"
    echo "   Windows (Chocolatey): choco install git-lfs"
    echo "   macOS: brew install git-lfs"
    echo "   Linux: sudo apt-get install git-lfs"
    echo ""
    echo "After installation, run this script again."
    exit 1
fi
echo "✅ Git LFS is installed"
echo ""

# Step 2: Initialize Git LFS
echo "⚙️ Initializing Git LFS..."
git lfs install
echo "✅ Git LFS initialized"
echo ""

# Step 3: Verify .gitattributes exists and has LFS patterns
echo "📋 Configuring .gitattributes..."
if [ ! -f ".gitattributes" ]; then
    echo "Creating .gitattributes..."
    cat > .gitattributes << 'EOF'
# Git LFS Configuration for Large Model Files
*.h5 filter=lfs diff=lfs merge=lfs -text
*.pb filter=lfs diff=lfs merge=lfs -text
*.tflite filter=lfs diff=lfs merge=lfs -text
*.onnx filter=lfs diff=lfs merge=lfs -text
*.pth filter=lfs diff=lfs merge=lfs -text
*.pkl filter=lfs diff=lfs merge=lfs -text
EOF
    echo "✅ Created .gitattributes"
else
    echo "✅ .gitattributes already exists"
fi
echo ""

# Step 4: Check for large model files
echo "🔍 Scanning for large model files..."
found_models=false
for pattern in "*.h5" "*.tflite" "*.pb" "*.onnx" "*.pth" "*.pkl"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            echo "   Found: $file ($size)"
            found_models=true
        fi
    done
done

if [ "$found_models" = false ]; then
    echo "   ℹ️ No large model files found in current directory"
fi
echo ""

# Step 5: Commit .gitattributes
echo "💾 Committing .gitattributes..."
git add .gitattributes
if git diff --cached --quiet .gitattributes; then
    echo "ℹ️ .gitattributes unchanged"
else
    git commit -m "Configure Git LFS for model files (*.h5, *.tflite, *.pb, *.onnx, *.pth, *.pkl)"
    echo "✅ Committed .gitattributes"
fi
echo ""

# Step 6: Summary
echo "🎉 Git LFS Setup Complete!"
echo ""
echo "📌 Next Steps:"
echo "1. Add your large files: git add <file>"
echo "2. Commit: git commit -m 'Add model files'"
echo "3. Push: git push origin main"
echo ""
echo "Git LFS will automatically handle uploads to GitHub's LFS server."
echo ""
