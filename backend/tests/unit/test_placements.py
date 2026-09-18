from datetime import datetime, timezone

from app.modules.placements.models import Company, PlacementOpportunity
from app.modules.placements.service import PlacementService


def test_create_opportunity_from_data_normalizes_placement_information():
    service = PlacementService(None, None, None)

    deadline = datetime(2026, 10, 15, 23, 59, tzinfo=timezone.utc)

    opportunity = service.create_opportunity_from_data(
        company_id=1,
        title="Software Engineer",
        description="Software engineering opportunity",
        eligibility_criteria="CGPA >= 7.0, no active backlogs",
        location="Bangalore",
        package_details="₹40,000/month",
        application_deadline=deadline,
        recruitment_status="open",
        sync_run_id=10,
    )

    assert opportunity.company_id == 1
    assert opportunity.title == "Software Engineer"
    assert opportunity.description == "Software engineering opportunity"
    assert opportunity.eligibility_criteria == "CGPA >= 7.0, no active backlogs"
    assert opportunity.location == "Bangalore"
    assert opportunity.package_details == "₹40,000/month"
    assert opportunity.application_deadline == deadline
    assert opportunity.recruitment_status == "open"
    assert opportunity.source_sync_run_id == 10


def test_updated_placement_values_are_supported():
    service = PlacementService(None, None, None)

    opportunity = service.create_opportunity_from_data(
        company_id=1,
        title="Software Engineer",
        description="Original description",
        eligibility_criteria="CGPA >= 7.0",
        location="Bangalore",
        package_details="6 LPA",
        application_deadline=None,
    )

    opportunity.title = "Graduate Software Engineer"
    opportunity.description = "Updated description"
    opportunity.eligibility_criteria = "CGPA >= 7.5"
    opportunity.recruitment_status = "closed"

    assert opportunity.title == "Graduate Software Engineer"
    assert opportunity.description == "Updated description"
    assert opportunity.eligibility_criteria == "CGPA >= 7.5"
    assert opportunity.recruitment_status == "closed"


def test_company_and_opportunity_have_consistent_relationship():
    company = Company(
        name="TechCorp Solutions",
        description="Technology company",
        industry="Information Technology",
    )

    opportunity = PlacementOpportunity(
        company=company,
        title="Software Engineer Intern",
        eligibility_criteria="CGPA >= 7.0",
        recruitment_status="open",
    )

    assert opportunity.company.name == "TechCorp Solutions"
    assert opportunity.company.industry == "Information Technology"