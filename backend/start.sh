#!/bin/bash

# SNOUTIQ Backend Startup Script

echo "🚀 Starting SNOUTIQ Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and add your API key"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if datasets exist
dataset_count=$(ls -1 datasets/master_*_dataset.json 2>/dev/null | wc -l)
if [ $dataset_count -eq 0 ]; then
    echo "⚠️  Warning: No dataset files found in datasets/"
    echo "Please add your JSON dataset files to backend/datasets/"
    exit 1
fi

echo "✅ Found $dataset_count dataset files"

# Start the server
echo "🚀 Starting Flask API..."
python app.py
