from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import Education


def _create_education(session: Session, **overrides) -> Education:
    defaults = dict(
        school="MIT",
        degree="BSc",
        field_of_study="Computer Science",
        start_year=2018,
        end_year=2022,
    )
    defaults.update(overrides)
    education = Education(**defaults)
    session.add(education)
    session.commit()
    session.refresh(education)
    return education


def test_edit_form_renders_prefilled_with_existing_values(
    client: TestClient, session: Session
):
    education = _create_education(session)

    response = client.get(f"/education/{education.id}/edit")

    assert response.status_code == 200
    assert "MIT" in response.text
    assert "BSc" in response.text
    assert "Computer Science" in response.text
    assert "2018" in response.text
    assert "2022" in response.text


def test_edit_form_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.get("/education/999/edit")

    assert response.status_code == 404


def test_update_saves_changes_to_existing_row_and_redirects_to_portfolio(
    client: TestClient, session: Session
):
    education = _create_education(session)

    response = client.post(
        f"/education/{education.id}/update",
        data={
            "school": "Stanford",
            "degree": "MSc",
            "field_of_study": "Data Science",
            "start_year": "2022",
            "end_year": "2024",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    # No new row was created: still exactly one row, now with updated values.
    rows = session.exec(select(Education)).all()
    assert len(rows) == 1
    assert rows[0].id == education.id
    assert rows[0].school == "Stanford"
    assert rows[0].degree == "MSc"
    assert rows[0].field_of_study == "Data Science"
    assert rows[0].start_year == 2022
    assert rows[0].end_year == 2024

    portfolio = client.get("/")
    assert "Stanford" in portfolio.text
    assert "MSc" in portfolio.text


def test_update_allows_all_fields_blank(client: TestClient, session: Session):
    education = _create_education(session)

    response = client.post(
        f"/education/{education.id}/update",
        data={
            "school": "",
            "degree": "",
            "field_of_study": "",
            "start_year": "",
            "end_year": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    session.refresh(education)
    assert education.school is None
    assert education.start_year is None


def test_update_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post(
        "/education/999/update",
        data={"school": "Stanford"},
        follow_redirects=False,
    )

    assert response.status_code == 404


def test_modifier_link_visible_on_portfolio_view(client: TestClient, session: Session):
    education = _create_education(session)

    response = client.get("/")

    assert response.status_code == 200
    assert f"/education/{education.id}/edit" in response.text


def test_delete_removes_the_row_via_post(client: TestClient, session: Session):
    education = _create_education(session)

    response = client.post(
        f"/education/{education.id}/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert session.exec(select(Education)).all() == []


def test_delete_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post("/education/999/delete", follow_redirects=False)

    assert response.status_code == 404
