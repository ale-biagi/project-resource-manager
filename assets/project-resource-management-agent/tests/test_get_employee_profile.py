"""Tests confirming sap-sf-employee-profile MCP server has been intentionally removed.

This server was removed to comply with the platform's 5-MCP-server limit.
Employee profile data (education, certifications, work experience) is considered
less critical than skills matching and time-off conflict detection for the core
project resource management workflow.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestGetEmployeeProfile:
    """Tests confirming employee profile server removal and remaining coverage."""

    def test_employee_profile_server_not_in_mock(self):
        """Verify sap-sf-employee-profile has been removed from mcp-mock.json."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        assert "sap-sf-employee-profile" not in mock_data["servers"], \
            "sap-sf-employee-profile must not be present (removed due to platform MCP limit)"

    def test_total_servers_is_five(self):
        """Verify total MCP server count is exactly 5 (platform limit)."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        assert len(mock_data["servers"]) == 5

    def test_skills_server_covers_core_employee_data(self):
        """Verify skills management server is present as the primary SF employee data source."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        assert "sap-sf-skills-management" in mock_data["servers"]
        server = mock_data["servers"]["sap-sf-skills-management"]
        assert "list_skillprofile_for_sfodata" in server["tools"]
        assert "list_ratedskillmapping_for_sfodata" in server["tools"]

    def test_skills_profiles_have_employee_ids(self):
        """Verify skill profiles contain employee identifiers."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        profiles = mock_data["servers"]["sap-sf-skills-management"]["tools"][
            "list_skillprofile_for_sfodata"
        ]["mock_response"]["d"]["results"]
        assert len(profiles) >= 2
        for profile in profiles:
            assert "externalCode" in profile
            assert profile["externalCode"].startswith("EMP")

    def test_time_off_server_present_as_availability_source(self):
        """Verify time-off server is present for availability conflict detection."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        assert "sap-sf-time-off" in mock_data["servers"]

    @pytest.mark.asyncio
    async def test_skills_data_sufficient_for_candidate_ranking(self):
        """Verify skills data provides enough detail for candidate scoring."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        rated_skills = mock_data["servers"]["sap-sf-skills-management"]["tools"][
            "list_ratedskillmapping_for_sfodata"
        ]["mock_response"]["d"]["results"]
        assert len(rated_skills) >= 2
        for skill in rated_skills:
            assert "skill" in skill
            assert "SkillProfile_externalCode" in skill
            assert "expectedLevel_en_US" in skill
