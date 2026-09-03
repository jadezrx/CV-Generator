from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import Language


def _create_language(session: Session, **overrides) -> Language:
    defaults = dict(
        language_name="Français",
        level="Courant",
    )
    defaults.update(overrides)
    language = Language(**defaults)
    session.add(language)
    session.commit()
    session.refresh(language)
    return language


def test_edit_form_renders_prefilled_with_existing_values(
    client: TestClient, session: Session
):
    language = _create_language(session)

    response = client.get(f"/languages/{language.id}/edit")

    assert response.status_code == 200
    assert "Français" in response.text
    assert "Courant" in response.text


def test_edit_form_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.get("/languages/999/edit")

    assert response.status_code == 404


def test_update_saves_changes_to_existing_row_and_redirects_to_portfolio(
    client: TestClient, session: Session
):
    language = _create_language(session)

    response = client.post(
        f"/languages/{language.id}/update",
        data={"language_name": "Anglais", "level": "Avancé"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/manage"

    # No new row was created: still exactly one row, now with updated values.
    rows = session.exec(select(Language)).all()
    assert len(rows) == 1
    assert rows[0].id == language.id
    assert rows[0].language_name == "Anglais"
    assert rows[0].level == "Avancé"

    portfolio = client.get("/")
    assert "Anglais" in portfolio.text
    assert "Avancé" in portfolio.text


def test_update_allows_all_fields_blank(client: TestClient, session: Session):
    language = _create_language(session)

    response = client.post(
        f"/languages/{language.id}/update",
        data={"language_name": "", "level": ""},
        follow_redirects=False,
    )

    assert response.status_code == 303
    session.refresh(language)
    assert language.language_name is None
    assert language.level is None


def test_update_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post(
        "/languages/999/update",
        data={"language_name": "Anglais"},
        follow_redirects=False,
    )

    assert response.status_code == 404


def test_modifier_link_visible_on_manage_view(client: TestClient, session: Session):
    language = _create_language(session)

    response = client.get("/manage")

    assert response.status_code == 200
    assert f"/languages/{language.id}/edit" in response.text


def test_modifier_link_not_visible_on_public_portfolio_view(
    client: TestClient, session: Session
):
    language = _create_language(session)

    response = client.get("/")

    assert response.status_code == 200
    assert f"/languages/{language.id}/edit" not in response.text


def test_delete_removes_the_row_via_post(client: TestClient, session: Session):
    language = _create_language(session)

    response = client.post(
        f"/languages/{language.id}/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/manage"
    assert session.exec(select(Language)).all() == []


def test_delete_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post("/languages/999/delete", follow_redirects=False)

    assert response.status_code == 404
