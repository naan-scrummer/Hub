from app.modules.placements.models import Company, PlacementContribution
from app.modules.placements.service import PlacementService


def test_new_contribution_is_unpublished_by_default():
    service = PlacementService(None, None, None)

    contribution = service.create_contribution_from_data(
        student_id=1,
        company_id=1,
        title="Interview Experience",
        content="Technical and HR interview experience.",
        contribution_type="interview_experience",
    )

    assert contribution.student_id == 1
    assert contribution.company_id == 1
    assert contribution.title == "Interview Experience"
    assert contribution.content == "Technical and HR interview experience."
    assert contribution.contribution_type == "interview_experience"
    assert contribution.is_published is False


def test_preparation_contribution_is_unpublished_by_default():
    service = PlacementService(None, None, None)

    contribution = service.create_contribution_from_data(
        student_id=2,
        company_id=2,
        title="Preparation Resources",
        content="Resources for aptitude and technical preparation.",
        contribution_type="preparation_resource",
    )

    assert contribution.contribution_type == "preparation_resource"
    assert contribution.is_published is False


def test_accepted_contribution_can_be_published():
    service = PlacementService(None, None, None)

    contribution = service.create_contribution_from_data(
        student_id=3,
        company_id=3,
        title="Interview Tips",
        content="Tips for technical and HR rounds.",
        contribution_type="tips",
    )

    contribution.is_published = True

    assert contribution.is_published is True


def test_unpublished_contribution_is_not_published_content():
    company = Company(name="TechCorp Solutions")

    contribution = PlacementContribution(
        student_id=4,
        company=company,
        title="Interview Experience",
        content="My interview experience.",
        contribution_type="interview_experience",
        is_published=False,
    )

    assert contribution.is_published is False