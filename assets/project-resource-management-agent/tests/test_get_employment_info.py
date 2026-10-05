"""Tests confirming sap-sf-employment-information MCP server has been intentionally removed.

This server was removed to comply with the platform's 5-MCP-server limit.
Employment information data (job title, department, location) is considered
less critical than skills matching and time-off conflict detection for the core
project resource management workflow.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestGetEmploymentInfo:
    """Tests confirming employment information server removal and remaining coverage."""

    def test_employment_info_server_not_in_mock(self):
        """Verify sap-sf-employment-information has been removed from mcp-mock.json."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        assert "sap-sf-employment-information" not in mock_data["servers"], \
            "sap-sf-employment-information must not be present (removed due to platform MCP limit)"

    def test_total_servers_is_five(self):
        """Verify total MCP server count is exactly 5 (platform limit)."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        assert len(mock_data["servers"]) == 5

    def test_availability_server_covers_workforce_data(self):
        """Verify workforce availability server is present as the primary capacity source."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        assert "sap-s4-workforce-daily-availability" in mock_data["servers"]
        server = mock_data["servers"]["sap-s4-workforce-daily-availability"]
        assert "list_timeoverviewset_for_shcm_api_manage_wf_availability" in server["tools"]

    def test_availability_records_have_employee_identifiers(self):
        """Verify availability records contain employee work agreement IDs."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        records = mock_data["servers"]["sap-s4-workforce-daily-availability"]["tools"][
            "list_timeoverviewset_for_shcm_api_manage_wf_availability"
        ]["mock_response"]["d"]["results"]
        assert len(records) >= 2
        for record in records:
            assert "Personworkagreementexternalid" in record
            assert "Plannedworkinghours" in record
            assert "Absencehours" in record

    def test_availability_includes_partial_availability_employee(self):
        """Verify mock data includes an employee with partial availability."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        records = mock_data["servers"]["sap-s4-workforce-daily-availability"]["tools"][
            "list_timeoverviewset_for_shcm_api_manage_wf_availability"
        ]["mock_response"]["d"]["results"]
        partial = [r for r in records if float(r["Absencehours"]) > 0]
        assert len(partial) >= 1, "At least one employee should have partial absence"

    @pytest.mark.asyncio
    async def test_skills_and_availability_sufficient_for_scoring(self):
        """Verify the remaining 3-criteria scoring model has all necessary data."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)

        # Criteria 1: Skills (50%)
        assert "sap-sf-skills-management" in mock_data["servers"]
        assert "list_ratedskillmapping_for_sfodata" in \
            mock_data["servers"]["sap-sf-skills-management"]["tools"]

        # Criteria 2: Availability (30%)
        assert "sap-s4-workforce-daily-availability" in mock_data["servers"]
        assert "list_timeoverviewset_for_shcm_api_manage_wf_availability" in \
            mock_data["servers"]["sap-s4-workforce-daily-availability"]["tools"]

        # Criteria 3: Time-off clearance (20%)
        assert "sap-sf-time-off" in mock_data["servers"]
        assert "list_employeetime_for_sfodata" in \
            mock_data["servers"]["sap-sf-time-off"]["tools"]

    def test_multiple_employees_in_availability_data(self):
        """Verify availability data covers multiple distinct employees."""
        mock_path = Path(__file__).parent.parent / "mcp-mock.json"
        with open(mock_path) as f:
            mock_data = json.load(f)
        records = mock_data["servers"]["sap-s4-workforce-daily-availability"]["tools"][
            "list_timeoverviewset_for_shcm_api_manage_wf_availability"
        ]["mock_response"]["d"]["results"]
        emp_ids = {r["Personworkagreementexternalid"] for r in records}
        assert len(emp_ids) >= 2, "Should have data for at least 2 distinct employees"
