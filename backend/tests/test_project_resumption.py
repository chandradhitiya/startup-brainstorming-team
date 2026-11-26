import io
import json
import pytest
from app import create_app
from app.models.project import ProjectManager, ProjectStatus
from app.services.report_agent import ReportManager, ReportOutline, ReportSection, ReportAgent


def test_resume_ontology_generation_without_reupload(tmp_path, monkeypatch):
    monkeypatch.setattr(ProjectManager, "PROJECTS_DIR", str(tmp_path))

    # Create an initial project with saved extracted text
    project = ProjectManager.create_project(name="Test Resume Project")
    project.simulation_requirement = "Simulate market trends"
    project.status = ProjectStatus.FAILED
    project.error = "Previous provider timeout"
    ProjectManager.save_project(project)
    ProjectManager.save_extracted_text(project.project_id, "Sample extracted document text from previous run.")

    # Mock OntologyGenerator
    class MockGenerator:
        def generate(self, document_texts, simulation_requirement, additional_context=None):
            assert document_texts == ["Sample extracted document text from previous run."]
            assert simulation_requirement == "Simulate market trends"
            return {
                "entity_types": [{"name": "Company"}],
                "edge_types": [{"name": "CompetesWith"}],
                "analysis_summary": "Extracted ontology successfully"
            }

    from app.api import graph as graph_api
    monkeypatch.setattr(graph_api, "OntologyGenerator", MockGenerator)

    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()

    # Call ontology generation providing only project_id (no new file uploads)
    response = client.post(
        "/api/graph/ontology/generate",
        data={"project_id": project.project_id},
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    res_data = response.json
    assert res_data["success"] is True
    assert res_data["data"]["project_id"] == project.project_id

    # Verify project state was updated
    refreshed = ProjectManager.get_project(project.project_id)
    assert refreshed.status == ProjectStatus.ONTOLOGY_GENERATED
    assert refreshed.error is None
    assert len(refreshed.ontology["entity_types"]) == 1


def test_report_agent_reuses_existing_outline(tmp_path, monkeypatch):
    monkeypatch.setattr(ReportManager, "REPORTS_DIR", str(tmp_path / "reports"))

    report_id = "test_report_resume"
    ReportManager._ensure_report_folder(report_id)

    # Save an existing outline
    saved_outline = ReportOutline(
        title="Saved Outline Title",
        summary="Saved Outline Summary",
        sections=[
            ReportSection(title="Existing Section 1", content=""),
            ReportSection(title="Existing Section 2", content="")
        ]
    )
    ReportManager.save_outline(report_id, saved_outline)

    # Instantiate ReportAgent
    agent = ReportAgent(
        simulation_id="sim_mock",
        graph_id="graph_mock",
        simulation_requirement="Test requirement"
    )

    # Mock plan_outline to fail if called
    def failing_plan(*args, **kwargs):
        raise AssertionError("plan_outline should not have been called when an outline exists!")

    monkeypatch.setattr(agent, "plan_outline", failing_plan)

    # Mock _generate_section_react so report generation finishes cleanly
    def mock_section_gen(section, *args, **kwargs):
        return f"Generated content for {section.title}"

    monkeypatch.setattr(agent, "_generate_section_react", mock_section_gen)

    # Run report generation
    report = agent.generate_report(report_id=report_id)

    assert report.outline.title == "Saved Outline Title"
    assert len(report.outline.sections) == 2
    assert "Existing Section 1" in report.markdown_content
