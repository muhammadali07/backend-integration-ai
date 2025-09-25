# Candidate Evaluation Backend

An AI-powered backend system for evaluating candidates' CVs and project reports using Large Language Models (LLM) and vector databases for Retrieval-Augmented Generation (RAG).

## 🚀 Features

- **File Upload & Processing**: Support for PDF, DOCX, and TXT files
- **AI-Powered Evaluation**: Integration with OpenAI GPT, Google Gemini, or mock responses
- **Vector Database**: ChromaDB for contextual information retrieval (RAG)
- **Asynchronous Processing**: Non-blocking evaluation with job queuing
- **Resilient Architecture**: Comprehensive error handling, retries, and fallback mechanisms
- **RESTful API**: Clean, documented endpoints with FastAPI
- **Real-time Status**: Job tracking and progress monitoring

## 📋 Requirements

- Python 3.8+
- FastAPI
- ChromaDB
- OpenAI API key (optional)
- Google Gemini API key (optional)

## 🛠️ Installation & Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd backend-integration-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# LLM Configuration
LLM_PROVIDER=mock  # Options: openai, gemini, mock
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_EXTENSIONS=pdf,docx,txt
UPLOAD_DIR=uploads

# Vector Database Configuration
VECTOR_DB_PATH=./chroma_db
```

### 4. Run the Application
```bash
python main.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Health Check
```http
GET /
```
**Response:**
```json
{
  "message": "Candidate Evaluation Backend is running",
  "version": "1.0.0"
}
```

#### 2. Upload Files
```http
POST /upload
POST /upload/cv
POST /upload/project
```

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF, DOCX, or TXT)

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "document.pdf",
  "message": "File uploaded successfully"
}
```

#### 3. Start Evaluation
```http
POST /evaluate
```

**Request Body:**
```json
{
  "cv_file_id": "uuid-string",
  "project_file_id": "uuid-string",
  "job_requirements": "Software Engineer position requiring Python, FastAPI, and AI experience..."
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "message": "Evaluation started successfully"
}
```

#### 4. Get Evaluation Results
```http
GET /result/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "result": {
    "cv_evaluation": {
      "technical_skills_score": 85,
      "experience_score": 78,
      "education_score": 90,
      "overall_score": 84,
      "strengths": ["Strong Python skills", "Relevant AI experience"],
      "weaknesses": ["Limited cloud experience"],
      "recommendations": ["Consider cloud computing training"]
    },
    "project_evaluation": {
      "technical_implementation_score": 88,
      "code_quality_score": 82,
      "documentation_score": 75,
      "innovation_score": 80,
      "overall_score": 81,
      "strengths": ["Clean architecture", "Good testing practices"],
      "weaknesses": ["Documentation could be improved"],
      "recommendations": ["Add more comprehensive documentation"]
    },
    "overall_summary": "Strong candidate with excellent technical skills...",
    "final_recommendation": "Recommended for interview"
  }
}
```

#### 5. Get Job Statistics
```http
GET /evaluate/stats
```

**Response:**
```json
{
  "total_jobs": 150,
  "completed_jobs": 145,
  "failed_jobs": 3,
  "pending_jobs": 2
}
```

#### 6. Delete Job
```http
DELETE /result/{job_id}
```

## 🏗️ Architecture & Design

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Upload   │    │   Evaluation    │    │     Results     │
│    Service      │    │    Service      │    │    Service      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                         │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File System   │    │   LLM Service   │    │  Vector Store   │
│    Storage      │    │ (OpenAI/Gemini) │    │   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Design Decisions

#### 1. **Modular Architecture**
- **Services Layer**: Separate services for file handling, LLM integration, vector operations, and evaluation orchestration
- **Routers Layer**: Clean API endpoint organization
- **Models Layer**: Pydantic schemas for request/response validation
- **Core Layer**: Shared utilities, configuration, and error handling

#### 2. **Asynchronous Processing**
- Non-blocking evaluation endpoints using background tasks
- Job status tracking with unique identifiers
- Prevents timeout issues for long-running AI operations

#### 3. **Resilience & Error Handling**
- **Retry Logic**: Exponential backoff with jitter for transient failures
- **Fallback Mechanisms**: Mock responses when AI services are unavailable
- **Custom Exceptions**: Structured error handling with detailed logging
- **Graceful Degradation**: System continues operating even with partial failures

#### 4. **Vector Database Integration (RAG)**
- ChromaDB for storing job descriptions and evaluation criteria
- Semantic search for relevant context retrieval
- Enhances AI evaluation accuracy with domain-specific knowledge

#### 5. **Multi-LLM Support**
- Pluggable LLM providers (OpenAI, Gemini, Mock)
- Consistent interface across different AI services
- Easy switching between providers via configuration

### File Structure

```
backend-integration-ai/
├── app/
│   ├── core/                 # Core utilities and configuration
│   │   ├── config.py        # Application settings
│   │   ├── exceptions.py    # Custom exception classes
│   │   └── retry.py         # Retry logic utilities
│   ├── models/              # Data models and schemas
│   │   └── schemas.py       # Pydantic models
│   ├── routers/             # API route handlers
│   │   ├── upload.py        # File upload endpoints
│   │   ├── evaluation.py    # Evaluation endpoints
│   │   └── results.py       # Results endpoints
│   └── services/            # Business logic services
│       ├── file_service.py      # File handling operations
│       ├── llm_service.py       # LLM integration
│       ├── vector_service.py    # Vector database operations
│       └── evaluation_service.py # Evaluation orchestration
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration Options

### LLM Providers
- **OpenAI**: Set `LLM_PROVIDER=openai` and provide `OPENAI_API_KEY`
- **Gemini**: Set `LLM_PROVIDER=gemini` and provide `GEMINI_API_KEY`
- **Mock**: Set `LLM_PROVIDER=mock` for testing without API keys

### File Upload Limits
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 10MB)
- `ALLOWED_EXTENSIONS`: Comma-separated list of allowed file extensions

### Vector Database
- `VECTOR_DB_PATH`: Directory for ChromaDB persistence

## 🧪 Testing

### Manual Testing
1. Start the server: `python main.py`
2. Visit http://localhost:8000/docs for interactive API testing
3. Upload test files and run evaluations

### Example Test Flow
```bash
# 1. Upload CV
curl -X POST "http://localhost:8000/api/v1/upload/cv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_cv.pdf"

# 2. Upload Project Report
curl -X POST "http://localhost:8000/api/v1/upload/project" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_project.pdf"

# 3. Start Evaluation
curl -X POST "http://localhost:8000/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_file_id": "cv-file-id",
    "project_file_id": "project-file-id",
    "job_requirements": "Python developer with AI experience"
  }'

# 4. Check Results
curl "http://localhost:8000/api/v1/result/{job_id}"
```

## 🚀 Production Deployment

### Environment Variables
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
LLM_PROVIDER=openai
OPENAI_API_KEY=your_production_key
```

### Security Considerations
- Configure CORS origins appropriately
- Use environment variables for sensitive data
- Implement authentication/authorization as needed
- Set up proper logging and monitoring

### Scaling Considerations
- Use Redis for job queue in multi-instance deployments
- Consider database persistence for job results
- Implement rate limiting for API endpoints
- Use load balancers for high availability

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues, please create an issue in the repository or contact the development team.