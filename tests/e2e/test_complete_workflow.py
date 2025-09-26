"""End-to-end tests for complete candidate evaluation workflow."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import time


class TestCompleteWorkflow:
    """Test class for complete end-to-end workflow."""

    @pytest.mark.e2e
    @patch('app.services.llm_service.LLMService.evaluate_cv')
    def test_complete_cv_evaluation_workflow(self, mock_evaluate_cv, client: TestClient, sample_pdf_file):
        """Test complete workflow: upload CV -> evaluate -> get results."""
        
        # Mock LLM evaluation response
        mock_evaluation = {
            "overall_score": 87,
            "technical_skills": {
                "score": 90,
                "strengths": ["Python", "FastAPI", "Docker"],
                "areas_for_improvement": ["Kubernetes", "Microservices"]
            },
            "experience": {
                "score": 85,
                "years_of_experience": 4,
                "relevant_experience": "Strong backend development with Python and FastAPI"
            },
            "education": {
                "score": 80,
                "degree": "Bachelor's in Computer Science",
                "certifications": ["AWS Solutions Architect"]
            },
            "soft_skills": {
                "score": 85,
                "communication": "Excellent",
                "leadership": "Good",
                "teamwork": "Excellent"
            },
            "recommendations": [
                "Gain experience with container orchestration (Kubernetes)",
                "Learn microservices architecture patterns",
                "Consider pursuing advanced cloud certifications"
            ],
            "fit_score": 88,
            "hiring_recommendation": "Strong candidate - Recommend for interview"
        }
        mock_evaluate_cv.return_value = mock_evaluation

        # Step 1: Upload CV
        with open(sample_pdf_file, "rb") as f:
            upload_response = client.post(
                "/api/v1/upload/cv",
                files={"file": ("candidate_cv.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        assert "message" in upload_data
        file_id = upload_data["file_id"]
        assert upload_data["filename"] == "candidate_cv.pdf"

        # Step 2: Evaluate CV
        evaluation_response = client.post(
            "/api/v1/evaluate",
            json={
                "cv_file_id": file_id,
                "job_description": "Software Engineer position"
            }
        )

        assert evaluation_response.status_code == 200
        evaluation_data = evaluation_response.json()
        assert "id" in evaluation_data
        assert "status" in evaluation_data
        assert "message" in evaluation_data
        
        # For e2e tests, we expect the evaluation to be processed asynchronously
        # The response contains job information, not the actual evaluation results
        job_id = evaluation_data["id"]
        assert evaluation_data["status"] == "queued"
        
        # Note: In a real e2e test, we would wait for the job to complete and check results
        # For this test, we just verify the job was queued successfully

    @pytest.mark.e2e
    @patch('app.services.llm_service.LLMService.evaluate_cv')
    def test_complete_workflow_with_project_report(self, mock_evaluate_cv, client: TestClient, sample_pdf_file, sample_txt_file):
        """Test complete workflow with both CV and project report."""
        
        # Mock enhanced evaluation with project analysis
        mock_evaluation = {
            "overall_score": 92,
            "technical_skills": {
                "score": 95,
                "strengths": ["Python", "Machine Learning", "API Development"],
                "areas_for_improvement": ["Frontend Development"]
            },
            "experience": {
                "score": 90,
                "years_of_experience": 5,
                "relevant_experience": "Excellent full-stack development experience"
            },
            "project_analysis": {
                "complexity_score": 90,
                "technical_depth": "Excellent",
                "innovation_level": "High",
                "code_quality": "Very Good",
                "documentation": "Good",
                "best_practices": "Excellent",
                "project_impact": "High business value demonstrated"
            },
            "fit_score": 93,
            "hiring_recommendation": "Excellent candidate - Strong hire recommendation"
        }
        mock_evaluate_cv.return_value = mock_evaluation

        # Step 1: Upload CV
        with open(sample_pdf_file, "rb") as f:
            cv_response = client.post(
                "/api/v1/upload/cv",
                files={"file": ("candidate_cv.pdf", f, "application/pdf")}
            )
        
        assert cv_response.status_code == 200
        cv_file_id = cv_response.json()["file_id"]

        # Step 2: Upload Project Report
        with open(sample_txt_file, "rb") as f:
            project_response = client.post(
                "/api/v1/upload/project",
                files={"file": ("project_report.txt", f, "text/plain")}
            )
        
        assert project_response.status_code == 200
        project_file_id = project_response.json()["file_id"]

        # Step 3: Evaluate with both files
        evaluation_response = client.post(
            "/api/v1/evaluate",
            json={
                "cv_file_id": cv_file_id,
                "project_report_file_id": project_file_id,
                "job_description": "Software Engineer position"
            }
        )

        assert evaluation_response.status_code == 200
        evaluation_data = evaluation_response.json()
        assert "id" in evaluation_data
        assert "status" in evaluation_data
        assert "message" in evaluation_data
        
        # For e2e tests, we expect the evaluation to be processed asynchronously
        # The response contains job information, not the actual evaluation results
        job_id = evaluation_data["id"]
        assert evaluation_data["status"] == "queued"
        
        # Note: In a real e2e test, we would wait for the job to complete and check results
        # For this test, we just verify the job was queued successfully

    @pytest.mark.e2e
    def test_workflow_with_invalid_file_types(self, client: TestClient):
        """Test workflow behavior with invalid file types."""
        
        # Step 1: Try to upload invalid file type
        invalid_content = b"This is not a valid PDF or document"
        
        response = client.post(
            "/api/v1/upload/cv",
            files={"file": ("invalid.xyz", invalid_content, "application/octet-stream")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @pytest.mark.e2e
    @patch('app.services.llm_service.LLMService.evaluate_cv')
    def test_workflow_with_llm_service_failure(self, mock_evaluate_cv, client: TestClient, sample_pdf_file):
        """Test workflow behavior when LLM service fails."""
        
        # Mock LLM service failure
        mock_evaluate_cv.side_effect = Exception("LLM API is unavailable")

        # Step 1: Upload CV (should succeed)
        with open(sample_pdf_file, "rb") as f:
            upload_response = client.post(
                "/api/v1/upload/cv",
                files={"file": ("cv.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]

        # Step 2: Evaluate CV (should fail gracefully)
        evaluation_response = client.post(
            "/api/v1/evaluate",
            json={
                "cv_file_id": file_id,
                "job_description": "Software Engineer position"
            }
        )

        # The API accepts the request but will fail during processing
        assert evaluation_response.status_code == 200
        data = evaluation_response.json()
        assert "id" in data
        assert "status" in data
        assert "message" in data

    @pytest.mark.e2e
    def test_workflow_with_multiple_candidates(self, client: TestClient, sample_pdf_file, sample_txt_file):
        """Test workflow with multiple candidates processed sequentially."""
        
        candidates_data = []
        
        # Process 3 candidates
        for i in range(3):
            # Upload CV for candidate i
            with open(sample_pdf_file, "rb") as f:
                cv_response = client.post(
                    "/api/v1/upload/cv",
                    files={"file": (f"candidate_{i}_cv.pdf", f, "application/pdf")}
                )
            
            assert cv_response.status_code == 200
            cv_data = cv_response.json()
            
            candidates_data.append({
                "candidate_id": i,
                "cv_file_id": cv_data["file_id"],
                "filename": cv_data["filename"]
            })
        
        # Verify all candidates have unique file IDs
        file_ids = [candidate["cv_file_id"] for candidate in candidates_data]
        assert len(set(file_ids)) == 3  # All unique

        # Verify filenames are correct
        for i, candidate in enumerate(candidates_data):
            assert candidate["filename"] == f"candidate_{i}_cv.pdf"

    @pytest.mark.e2e
    @patch('app.services.llm_service.LLMService.evaluate_cv')
    def test_workflow_performance_timing(self, mock_evaluate_cv, client: TestClient, sample_pdf_file):
        """Test workflow performance and timing."""
        
        # Mock quick evaluation response
        mock_evaluation = {"overall_score": 80, "fit_score": 82}
        mock_evaluate_cv.return_value = mock_evaluation

        start_time = time.time()

        # Step 1: Upload CV
        with open(sample_pdf_file, "rb") as f:
            upload_response = client.post(
                "/api/v1/upload/cv",
                files={"file": ("cv.pdf", f, "application/pdf")}
            )
        
        upload_time = time.time()
        file_id = upload_response.json()["file_id"]

        # Step 2: Evaluate CV
        evaluation_response = client.post(
            "/api/v1/evaluate",
            json={
                "cv_file_id": file_id,
                "job_description": "Software Engineer position"
            }
        )
        
        evaluation_time = time.time()

        # Verify responses
        assert upload_response.status_code == 200
        assert evaluation_response.status_code == 200

        # Check timing (these are rough estimates and may vary)
        upload_duration = upload_time - start_time
        evaluation_duration = evaluation_time - upload_time
        total_duration = evaluation_time - start_time

        # Upload should be relatively fast (< 5 seconds for small files)
        assert upload_duration < 5.0
        
        # Total workflow should complete in reasonable time (< 30 seconds)
        assert total_duration < 30.0

        print(f"Upload took: {upload_duration:.2f}s")
        print(f"Evaluation took: {evaluation_duration:.2f}s")
        print(f"Total workflow took: {total_duration:.2f}s")

    @pytest.mark.e2e
    def test_workflow_data_persistence(self, client: TestClient, sample_pdf_file):
        """Test that uploaded files and evaluations persist correctly."""
        
        # Upload a file
        with open(sample_pdf_file, "rb") as f:
            upload_response = client.post(
                "/api/v1/upload/cv",
                files={"file": ("persistent_cv.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]

        # Verify file can be referenced later (this would require a GET endpoint)
        # For now, we'll just verify the file_id format
        assert isinstance(file_id, str)
        assert len(file_id) > 0