from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import ProfessionalExperience


def _create_experience(session: Session, **overrides) -> ProfessionalExperience:
    defaults = dict(
        company="Acme",
        position="Engineer",
        start_date=2020,
        end_date=2022,
        description="Built things.",
    )
    defaults.update(overrides)
    experience = ProfessionalExperience(**defaults)
    session.add(experience)
    session.commit()
    session.refresh(experience)
    return experience


def test_edit_form_renders_prefilled_with_existing_values(
    client: TestClient, session: Session
):
    experience = _create_experience(session)

    response = client.get(f"/professional_experience/{experience.id}/edit")

    assert response.status_code == 200
    assert "Acme" in response.text
    assert "Engineer" in response.text
    assert "2020" in response.text
    assert "2022" in response.text
    assert "Built things." in response.text


def test_edit_form_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.get("/professional_experience/999/edit")

    assert response.status_code == 404


def test_update_saves_changes_to_existing_row_and_redirects_to_portfolio(
    client: TestClient, session: Session
):
    experience = _create_experience(session)

    response = client.post(
        f"/professional_experience/{experience.id}/update",
        data={
            "company": "New Co",
            "position": "Senior Engineer",
            "start_date": "2021",
            "end_date": "2023",
            "description": "Did more things.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    # No new row was created: still exactly one row, now with updated values.
    rows = session.exec(select(ProfessionalExperience)).all()
    assert len(rows) == 1
    assert rows[0].id == experience.id
    assert rows[0].company == "New Co"
    assert rows[0].position == "Senior Engineer"
    assert rows[0].start_date == 2021
    assert rows[0].end_date == 2023
    assert rows[0].description == "Did more things."

    portfolio = client.get("/")
    assert "New Co" in portfolio.text
    assert "Senior Engineer" in portfolio.text


def test_update_allows_all_fields_blank(client: TestClient, session: Session):
    experience = _create_experience(session)

    response = client.post(
        f"/professional_experience/{experience.id}/update",
        data={
            "company": "",
            "position": "",
            "start_date": "",
            "end_date": "",
            "description": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    session.refresh(experience)
    assert experience.company is None
    assert experience.start_date is None


def test_update_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post(
        "/professional_experience/999/update",
        data={"company": "New Co"},
        follow_redirects=False,
    )

    assert response.status_code == 404


def test_modifier_link_visible_on_portfolio_view(client: TestClient, session: Session):
    experience = _create_experience(session)

    response = client.get("/")

    assert response.status_code == 200
    assert f"/professional_experience/{experience.id}/edit" in response.text
