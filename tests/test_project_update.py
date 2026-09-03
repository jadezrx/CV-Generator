from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import Project


def _create_project(session: Session, **overrides) -> Project:
    defaults = dict(
        name_project="CV Generator",
        description="Un générateur de portfolio",
        link="https://example.com/cv-generator",
    )
    defaults.update(overrides)
    project = Project(**defaults)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def test_edit_form_renders_prefilled_with_existing_values(
    client: TestClient, session: Session
):
    project = _create_project(session)

    response = client.get(f"/projects/{project.id}/edit")

    assert response.status_code == 200
    assert "CV Generator" in response.text
    assert "Un générateur de portfolio" in response.text
    assert "https://example.com/cv-generator" in response.text


def test_edit_form_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.get("/projects/999/edit")

    assert response.status_code == 404


def test_update_saves_changes_to_existing_row_and_redirects_to_portfolio(
    client: TestClient, session: Session
):
    project = _create_project(session)

    response = client.post(
        f"/projects/{project.id}/update",
        data={
            "name_project": "Portfolio v2",
            "description": "Refonte du site",
            "link": "https://example.com/v2",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    # No new row was created: still exactly one row, now with updated values.
    rows = session.exec(select(Project)).all()
    assert len(rows) == 1
    assert rows[0].id == project.id
    assert rows[0].name_project == "Portfolio v2"
    assert rows[0].description == "Refonte du site"
    assert rows[0].link == "https://example.com/v2"

    portfolio = client.get("/")
    assert "Portfolio v2" in portfolio.text
    assert "Refonte du site" in portfolio.text


def test_update_allows_all_fields_blank(client: TestClient, session: Session):
    project = _create_project(session)

    response = client.post(
        f"/projects/{project.id}/update",
        data={"name_project": "", "description": "", "link": ""},
        follow_redirects=False,
    )

    assert response.status_code == 303
    session.refresh(project)
    assert project.name_project is None
    assert project.description is None
    assert project.link is None


def test_update_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post(
        "/projects/999/update",
        data={"name_project": "Portfolio v2"},
        follow_redirects=False,
    )

    assert response.status_code == 404


def test_modifier_link_visible_on_portfolio_view(client: TestClient, session: Session):
    project = _create_project(session)

    response = client.get("/")

    assert response.status_code == 200
    assert f"/projects/{project.id}/edit" in response.text


def test_delete_removes_the_row_via_post(client: TestClient, session: Session):
    project = _create_project(session)

    response = client.post(
        f"/projects/{project.id}/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert session.exec(select(Project)).all() == []


def test_delete_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post("/projects/999/delete", follow_redirects=False)

    assert response.status_code == 404
