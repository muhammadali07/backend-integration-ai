"""Sample data and mock responses for testing."""

# Sample CV text content
SAMPLE_CV_TEXT = """
John Doe
Senior Software Engineer

Contact Information:
Email: john.doe@email.com
Phone: +1-555-0123
LinkedIn: linkedin.com/in/johndoe
GitHub: github.com/johndoe

Professional Summary:
Experienced software engineer with 5+ years of expertise in backend development, 
API design, and cloud technologies. Proven track record of building scalable 
applications using Python, FastAPI, and AWS services.

Technical Skills:
- Programming Languages: Python, JavaScript, Java, Go
- Frameworks: FastAPI, Django, Flask, React, Node.js
- Databases: PostgreSQL, MongoDB, Redis
- Cloud Platforms: AWS, Google Cloud Platform
- DevOps: Docker, Kubernetes, CI/CD, Jenkins
- Tools: Git, Jira, Confluence

Professional Experience:

Senior Software Engineer | TechCorp Inc. | 2021 - Present
- Led development of microservices architecture serving 1M+ users
- Implemented RESTful APIs using FastAPI with 99.9% uptime
- Optimized database queries resulting in 40% performance improvement
- Mentored junior developers and conducted code reviews

Software Engineer | StartupXYZ | 2019 - 2021
- Developed full-stack web applications using Python and React
- Integrated third-party APIs and payment systems
- Implemented automated testing and CI/CD pipelines
- Collaborated with cross-functional teams in Agile environment

Education:
Bachelor of Science in Computer Science
University of Technology | 2015 - 2019
GPA: 3.8/4.0

Certifications:
- AWS Certified Solutions Architect - Associate
- Certified Kubernetes Administrator (CKA)

Projects:
E-commerce Platform (2022)
- Built scalable e-commerce platform handling 10K+ concurrent users
- Technologies: Python, FastAPI, PostgreSQL, Redis, Docker
- Implemented real-time inventory management and payment processing

Task Management API (2021)
- Developed RESTful API for task management with real-time notifications
- Technologies: Python, FastAPI, WebSocket, MongoDB
- Achieved 99.5% API availability with comprehensive monitoring
"""

# Sample project report content
SAMPLE_PROJECT_TEXT = """
Project Report: E-commerce Platform Development

Project Overview:
This project involved developing a comprehensive e-commerce platform from scratch 
to handle high-traffic scenarios and provide seamless user experience.

Technical Architecture:
- Backend: Python with FastAPI framework
- Database: PostgreSQL for transactional data, Redis for caching
- Frontend: React.js with TypeScript
- Infrastructure: AWS ECS with Application Load Balancer
- Monitoring: CloudWatch, Prometheus, Grafana

Key Features Implemented:
1. User Authentication and Authorization
   - JWT-based authentication
   - Role-based access control (RBAC)
   - OAuth integration with Google and Facebook

2. Product Management System
   - CRUD operations for products and categories
   - Image upload and optimization
   - Inventory tracking with real-time updates

3. Shopping Cart and Checkout
   - Session-based cart management
   - Multiple payment gateway integration (Stripe, PayPal)
   - Order processing workflow

4. Real-time Features
   - WebSocket connections for live inventory updates
   - Push notifications for order status
   - Live chat support system

Performance Optimizations:
- Implemented Redis caching for frequently accessed data
- Database query optimization with proper indexing
- CDN integration for static assets
- API response compression and pagination

Security Measures:
- Input validation and sanitization
- SQL injection prevention
- Rate limiting and DDoS protection
- HTTPS enforcement with SSL certificates

Testing Strategy:
- Unit tests with 90%+ code coverage
- Integration tests for API endpoints
- Load testing with Apache JMeter
- Security testing with OWASP ZAP

Deployment and DevOps:
- Containerized application with Docker
- CI/CD pipeline with GitHub Actions
- Blue-green deployment strategy
- Automated rollback mechanisms

Results and Metrics:
- Successfully handles 10,000+ concurrent users
- 99.9% uptime achieved
- Average API response time: 150ms
- 40% reduction in page load times
- Zero security vulnerabilities in production

Challenges and Solutions:
1. Database Performance Issues
   - Challenge: Slow query performance under high load
   - Solution: Implemented connection pooling and query optimization

2. Scalability Concerns
   - Challenge: Application couldn't handle traffic spikes
   - Solution: Implemented horizontal scaling with load balancers

3. Real-time Data Synchronization
   - Challenge: Inventory inconsistencies across multiple instances
   - Solution: Implemented event-driven architecture with message queues

Future Enhancements:
- Machine learning-based product recommendations
- Advanced analytics and reporting dashboard
- Mobile application development
- International payment gateway integration

Technologies Used:
- Backend: Python 3.9, FastAPI 0.68, SQLAlchemy, Alembic
- Frontend: React 17, TypeScript, Material-UI
- Database: PostgreSQL 13, Redis 6
- Infrastructure: AWS ECS, RDS, ElastiCache, CloudFront
- Monitoring: CloudWatch, Prometheus, Grafana
- Testing: pytest, Jest, JMeter
"""

# Mock LLM evaluation responses
MOCK_CV_EVALUATION_BASIC = {
    "overall_score": 85,
    "technical_skills": {
        "score": 90,
        "strengths": [
            "Strong Python and FastAPI expertise",
            "Excellent cloud platform knowledge (AWS)",
            "Good understanding of microservices architecture",
            "Solid database experience (PostgreSQL, MongoDB, Redis)"
        ],
        "areas_for_improvement": [
            "Could benefit from more frontend development experience",
            "Machine learning skills would be valuable",
            "Consider gaining experience with other cloud platforms"
        ]
    },
    "experience": {
        "score": 88,
        "years_of_experience": 5,
        "relevant_experience": "Excellent backend development experience with proven track record of building scalable applications",
        "leadership_experience": "Demonstrated mentoring and code review experience",
        "project_complexity": "High - worked on systems serving 1M+ users"
    },
    "education": {
        "score": 80,
        "degree": "Bachelor of Science in Computer Science",
        "gpa": "3.8/4.0",
        "university": "University of Technology",
        "graduation_year": 2019,
        "relevant_coursework": "Strong foundation in computer science fundamentals"
    },
    "certifications": {
        "score": 85,
        "certifications": [
            "AWS Certified Solutions Architect - Associate",
            "Certified Kubernetes Administrator (CKA)"
        ],
        "relevance": "Highly relevant cloud and container orchestration certifications"
    },
    "soft_skills": {
        "score": 82,
        "communication": "Good - demonstrated through mentoring and collaboration",
        "leadership": "Developing - shows mentoring experience",
        "teamwork": "Excellent - worked in cross-functional Agile teams",
        "problem_solving": "Excellent - evidenced by performance optimizations"
    },
    "projects": {
        "score": 90,
        "project_quality": "High - demonstrates ability to build complex, scalable systems",
        "technical_depth": "Excellent - shows deep understanding of architecture and optimization",
        "innovation": "Good - implemented modern technologies and best practices"
    },
    "fit_score": 87,
    "hiring_recommendation": "Strong candidate - Recommend for technical interview",
    "recommendations": [
        "Excellent technical background with strong backend expertise",
        "Proven ability to work with high-scale systems",
        "Good leadership potential with mentoring experience",
        "Consider for senior backend engineer positions",
        "May benefit from frontend or full-stack role exposure"
    ],
    "red_flags": [],
    "strengths_summary": [
        "5+ years of relevant backend development experience",
        "Strong technical skills in Python, FastAPI, and cloud technologies",
        "Proven track record with high-scale applications",
        "Relevant certifications and continuous learning",
        "Leadership and mentoring experience"
    ]
}

MOCK_CV_EVALUATION_WITH_PROJECT = {
    "overall_score": 92,
    "technical_skills": {
        "score": 95,
        "strengths": [
            "Exceptional full-stack development capabilities",
            "Advanced system architecture and design skills",
            "Strong DevOps and infrastructure knowledge",
            "Excellent performance optimization expertise"
        ],
        "areas_for_improvement": [
            "Could explore machine learning integration",
            "Consider mobile development experience"
        ]
    },
    "experience": {
        "score": 90,
        "years_of_experience": 5,
        "relevant_experience": "Outstanding experience with complex, production-grade systems",
        "leadership_experience": "Strong technical leadership demonstrated through project execution",
        "project_complexity": "Very High - built enterprise-grade e-commerce platform"
    },
    "project_analysis": {
        "complexity_score": 95,
        "technical_depth": "Exceptional - demonstrates mastery of full-stack development",
        "architecture_quality": "Excellent - well-designed microservices architecture",
        "scalability_design": "Outstanding - handles 10K+ concurrent users",
        "security_implementation": "Excellent - comprehensive security measures",
        "performance_optimization": "Exceptional - achieved significant performance improvements",
        "testing_strategy": "Excellent - comprehensive testing with high coverage",
        "devops_practices": "Outstanding - modern CI/CD and deployment strategies",
        "documentation_quality": "Very Good - well-documented project with clear metrics",
        "innovation_level": "High - implemented modern technologies and best practices",
        "business_impact": "High - delivered measurable performance and reliability improvements",
        "code_quality_indicators": "Excellent - follows best practices and industry standards",
        "problem_solving_demonstration": "Outstanding - effectively solved complex technical challenges"
    },
    "education": {
        "score": 80,
        "degree": "Bachelor of Science in Computer Science",
        "gpa": "3.8/4.0",
        "university": "University of Technology",
        "graduation_year": 2019,
        "relevant_coursework": "Strong foundation in computer science fundamentals"
    },
    "certifications": {
        "score": 85,
        "certifications": [
            "AWS Certified Solutions Architect - Associate",
            "Certified Kubernetes Administrator (CKA)"
        ],
        "relevance": "Highly relevant and validates practical skills demonstrated in project"
    },
    "soft_skills": {
        "score": 88,
        "communication": "Excellent - clear project documentation and presentation",
        "leadership": "Strong - demonstrated through project management and technical decisions",
        "teamwork": "Excellent - worked effectively in cross-functional teams",
        "problem_solving": "Outstanding - evidenced by innovative solutions to complex challenges"
    },
    "projects": {
        "score": 95,
        "project_quality": "Outstanding - enterprise-grade solution with proven results",
        "technical_depth": "Exceptional - demonstrates mastery across full technology stack",
        "innovation": "High - implemented cutting-edge technologies and practices"
    },
    "fit_score": 94,
    "hiring_recommendation": "Excellent candidate - Strong hire recommendation for senior/lead positions",
    "recommendations": [
        "Exceptional technical capabilities across full stack",
        "Proven ability to deliver complex, high-impact projects",
        "Strong leadership and problem-solving skills",
        "Ideal for senior backend engineer or technical lead roles",
        "Consider for architecture or principal engineer track"
    ],
    "red_flags": [],
    "strengths_summary": [
        "Outstanding technical execution on complex project",
        "Comprehensive full-stack and DevOps expertise",
        "Proven ability to handle enterprise-scale challenges",
        "Strong focus on performance, security, and best practices",
        "Excellent documentation and communication skills",
        "Demonstrated leadership and technical decision-making"
    ]
}

# Mock error responses
MOCK_LLM_ERROR_RESPONSE = {
    "error": "LLM service unavailable",
    "message": "Unable to process evaluation at this time",
    "retry_after": 300
}

MOCK_INVALID_JSON_RESPONSE = "This is not a valid JSON response from LLM"

# Sample file metadata
SAMPLE_FILE_METADATA = {
    "pdf_file": {
        "filename": "sample_cv.pdf",
        "content_type": "application/pdf",
        "size": 245760,  # ~240KB
        "extension": ".pdf"
    },
    "txt_file": {
        "filename": "sample_document.txt",
        "content_type": "text/plain",
        "size": 5120,  # ~5KB
        "extension": ".txt"
    },
    "docx_file": {
        "filename": "sample_report.docx",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "size": 102400,  # ~100KB
        "extension": ".docx"
    }
}

# Test configuration constants
TEST_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_extensions": [".pdf", ".txt", ".docx"],
    "upload_timeout": 30,  # seconds
    "evaluation_timeout": 120,  # seconds
    "test_upload_dir": "/tmp/test_uploads"
}

# Mock API responses
MOCK_API_RESPONSES = {
    "upload_success": {
        "success": True,
        "message": "File uploaded successfully",
        "file_id": "test-file-id-123",
        "filename": "test_file.pdf"
    },
    "upload_error": {
        "success": False,
        "message": "File upload failed",
        "error": "Invalid file type"
    },
    "evaluation_success": {
        "success": True,
        "message": "CV evaluation completed",
        "evaluation_id": "eval-123",
        "evaluation": MOCK_CV_EVALUATION_BASIC
    },
    "evaluation_error": {
        "success": False,
        "message": "Evaluation failed",
        "error": "Internal server error"
    }
}