from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import Skill


def _create_skill(session: Session, **overrides) -> Skill:
    defaults = dict(
        software="Python",
        level="Avancé",
    )
    defaults.update(overrides)
    skill = Skill(**defaults)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


def test_edit_form_renders_prefilled_with_existing_values(
    client: TestClient, session: Session
):
    skill = _create_skill(session)

    response = client.get(f"/skills/{skill.id}/edit")

    assert response.status_code == 200
    assert "Python" in response.text
    assert "Avancé" in response.text


def test_edit_form_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.get("/skills/999/edit")

    assert response.status_code == 404


def test_update_saves_changes_to_existing_row_and_redirects_to_portfolio(
    client: TestClient, session: Session
):
    skill = _create_skill(session)

    response = client.post(
        f"/skills/{skill.id}/update",
        data={"software": "Rust", "level": "Intermédiaire"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    # No new row was created: still exactly one row, now with updated values.
    rows = session.exec(select(Skill)).all()
    assert len(rows) == 1
    assert rows[0].id == skill.id
    assert rows[0].software == "Rust"
    assert rows[0].level == "Intermédiaire"

    portfolio = client.get("/")
    assert "Rust" in portfolio.text
    assert "Intermédiaire" in portfolio.text


def test_update_allows_all_fields_blank(client: TestClient, session: Session):
    skill = _create_skill(session)

    response = client.post(
        f"/skills/{skill.id}/update",
        data={"software": "", "level": ""},
        follow_redirects=False,
    )

    assert response.status_code == 303
    session.refresh(skill)
    assert skill.software is None
    assert skill.level is None


def test_update_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post(
        "/skills/999/update",
        data={"software": "Rust"},
        follow_redirects=False,
    )

    assert response.status_code == 404


def test_modifier_link_visible_on_portfolio_view(client: TestClient, session: Session):
    skill = _create_skill(session)

    response = client.get("/")

    assert response.status_code == 200
    assert f"/skills/{skill.id}/edit" in response.text


def test_delete_removes_the_row_via_post(client: TestClient, session: Session):
    skill = _create_skill(session)

    response = client.post(
        f"/skills/{skill.id}/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert session.exec(select(Skill)).all() == []


def test_delete_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post("/skills/999/delete", follow_redirects=False)

    assert response.status_code == 404
