import pytest

from app.integrations.college_portal.interface import PlacementPortalAdapter
from app.integrations.college_portal.mock_adapters import (
    MockCollegePortalClient,
    MockPlacementPortalAdapter,
)


@pytest.mark.asyncio
async def test_mock_placement_adapter_returns_opportunities():
    client = MockCollegePortalClient()
    adapter = MockPlacementPortalAdapter(client)

    opportunities = await adapter.sync(sync_run_id=1)

    assert opportunities
    assert len(opportunities) == 3


@pytest.mark.asyncio
async def test_placement_data_is_mapped_to_domain_model():
    client = MockCollegePortalClient()
    adapter = MockPlacementPortalAdapter(client)

    opportunities = await adapter.sync(sync_run_id=1)

    opportunity = opportunities[0]

    assert opportunity.company_id == 1
    assert opportunity.title == "Software Engineer Intern"
    assert opportunity.description == "Summer internship program for CS students"
    assert opportunity.eligibility_criteria == (
        "CGPA >= 7.0, no active backlogs"
    )
    assert opportunity.location == "Bangalore"
    assert opportunity.package_details == "₹40,000/month"
    assert opportunity.recruitment_status == "open"
    assert opportunity.source_sync_run_id == 1


@pytest.mark.asyncio
async def test_placement_adapter_implements_supported_interface():
    client = MockCollegePortalClient()
    adapter = MockPlacementPortalAdapter(client)

    assert isinstance(adapter, PlacementPortalAdapter)


@pytest.mark.asyncio
async def test_placement_source_failure_is_detected():
    class FailingPlacementClient(MockCollegePortalClient):
        async def fetch_placements(self):
            raise RuntimeError("Placement source unavailable")

    client = FailingPlacementClient()
    adapter = MockPlacementPortalAdapter(client)

    with pytest.raises(RuntimeError, match="Placement source unavailable"):
        await adapter.sync(sync_run_id=1)