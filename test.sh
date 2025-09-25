#!/bin/bash

# Candidate Evaluation Backend - API Testing Script
# This script tests all API endpoints

set -e  # Exit on any error

BASE_URL="http://localhost:8000"

echo "🧪 Testing Candidate Evaluation Backend API..."

# Check if server is running
echo "🔍 Checking if server is running..."
if ! curl -s "$BASE_URL" > /dev/null; then
    echo "❌ Server is not running at $BASE_URL"
    echo "Please start the server first with './run.sh' or './dev.sh'"
    exit 1
fi

echo "✅ Server is running"

# Test root endpoint
echo ""
echo "📍 Testing root endpoint..."
curl -s "$BASE_URL" | jq '.' || echo "Response received"

# Test docs endpoint
echo ""
echo "📚 Testing documentation endpoint..."
curl -s -I "$BASE_URL/docs" | head -n 1

# Test evaluation stats
echo ""
echo "📊 Testing evaluation stats..."
curl -s "$BASE_URL/evaluate/stats" | jq '.' || echo "Response received"

# Test results endpoint (should return empty list initially)
echo ""
echo "📋 Testing results endpoint..."
curl -s "$BASE_URL/results" | jq '.' || echo "Response received"

# Create a test file for upload
echo ""
echo "📄 Creating test CV file..."
cat > test_cv.txt << EOF
John Doe
Software Engineer

Experience:
- 5 years of Python development
- FastAPI and Django experience
- Machine Learning projects
- Team leadership experience

Skills:
- Python, JavaScript, SQL
- Docker, Kubernetes
- AWS, GCP
- Agile methodologies

Education:
- Bachelor's in Computer Science
- Master's in Data Science
EOF

# Test file upload
echo ""
echo "📤 Testing CV upload..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/upload/cv" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@test_cv.txt")

echo "$UPLOAD_RESPONSE" | jq '.' || echo "Response: $UPLOAD_RESPONSE"

# Extract file_id from upload response
FILE_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.file_id' 2>/dev/null || echo "")

if [ "$FILE_ID" != "" ] && [ "$FILE_ID" != "null" ]; then
    echo "✅ File uploaded successfully with ID: $FILE_ID"
    
    # Test evaluation
    echo ""
    echo "🔄 Testing evaluation..."
    EVAL_RESPONSE=$(curl -s -X POST "$BASE_URL/evaluate" \
        -H "Content-Type: application/json" \
        -d "{
            \"cv_file_id\": \"$FILE_ID\",
            \"job_requirements\": \"Looking for a senior Python developer with FastAPI experience and team leadership skills\"
        }")
    
    echo "$EVAL_RESPONSE" | jq '.' || echo "Response: $EVAL_RESPONSE"
    
    # Extract job_id from evaluation response
    JOB_ID=$(echo "$EVAL_RESPONSE" | jq -r '.job_id' 2>/dev/null || echo "")
    
    if [ "$JOB_ID" != "" ] && [ "$JOB_ID" != "null" ]; then
        echo "✅ Evaluation started with Job ID: $JOB_ID"
        
        # Wait a bit for processing
        echo ""
        echo "⏳ Waiting for evaluation to process..."
        sleep 3
        
        # Test result retrieval
        echo ""
        echo "📊 Testing result retrieval..."
        curl -s "$BASE_URL/result/$JOB_ID" | jq '.' || echo "Response received"
        
        # Test job deletion
        echo ""
        echo "🗑️  Testing job deletion..."
        curl -s -X DELETE "$BASE_URL/result/$JOB_ID" | jq '.' || echo "Response received"
    else
        echo "⚠️  Could not extract job_id from evaluation response"
    fi
else
    echo "⚠️  Could not extract file_id from upload response"
fi

# Clean up test file
rm -f test_cv.txt

echo ""
echo "🎉 API testing completed!"
echo ""
echo "📖 For interactive testing, visit: $BASE_URL/docs"