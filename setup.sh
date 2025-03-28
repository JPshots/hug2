#!/bin/bash

# Create directory structure
mkdir -p framework
mkdir -p static

echo "Debugging directory structure..."
echo "Current directory contents:"
ls -la

echo "Contents of parent directory:"
ls -la ..

echo "Looking for JSON files..."
find . -name "*.json" -type f

# Check if framework_files directory exists
if [ -d "framework_files" ]; then
    echo "framework_files directory found"
    echo "Contents of framework_files directory:"
    ls -la framework_files/
    
    # Copy all JSON files from framework_files directory to framework directory
    echo "Copying framework files..."
    cp -v framework_files/*.json framework/
else
    echo "framework_files directory NOT found!"
    
    # Try to find the directory with framework files
    for dir in $(find . -type d | grep -v "framework$"); do
        if [ -n "$(find $dir -name "*.json" 2>/dev/null)" ]; then
            echo "Found JSON files in: $dir"
            echo "Contents of $dir:"
            ls -la $dir/
            
            echo "Copying from $dir to framework/"
            cp -v $dir/*.json framework/ 2>/dev/null || true
        fi
    done
fi

# List the copied files
echo "Framework files available in framework/ directory:"
ls -la framework/

echo "Setup complete!"