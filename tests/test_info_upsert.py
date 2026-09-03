from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import Info


def _info_payload(**overrides) -> dict:
    defaults = dict(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        phone="555-0100",
        location="London",
        linkedin="linkedin.com/in/ada",
        github="github.com/ada",
    )
    defaults.update(overrides)
    return defaults


def test_form_renders_empty_info_fields_when_none_exists(client: TestClient):
    response = client.get("/form")

    assert response.status_code == 200
    assert 'name="first_name" value=""' in response.text
    assert 'name="last_name" value=""' in response.text
    assert 'name="email" value=""' in response.text
    assert 'name="phone" value=""' in response.text
    assert 'name="location" value=""' in response.text
    assert 'name="github" value=""' in response.text
    assert 'name="linkedin" value=""' in response.text


def test_first_submission_creates_the_info_row(client: TestClient, session: Session):
    response = client.post("/info", data=_info_payload(), follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/form"

    rows = session.exec(select(Info)).all()
    assert len(rows) == 1
    assert rows[0].first_name == "Ada"
    assert rows[0].email == "ada@example.com"


def test_second_submission_updates_in_place_instead_of_creating_a_second_row(
    client: TestClient, session: Session
):
    client.post("/info", data=_info_payload(), follow_redirects=False)
    rows = session.exec(select(Info)).all()
    original_id = rows[0].id

    response = client.post(
        "/info",
        data=_info_payload(email="ada.lovelace@example.com"),
        follow_redirects=False,
    )

    assert response.status_code == 303

    rows = session.exec(select(Info)).all()
    assert len(rows) == 1
    assert rows[0].id == original_id
    assert rows[0].email == "ada.lovelace@example.com"
    # Every other field preserved as previously saved.
    assert rows[0].first_name == "Ada"
    assert rows[0].last_name == "Lovelace"
    assert rows[0].phone == "555-0100"
    assert rows[0].location == "London"
    assert rows[0].linkedin == "linkedin.com/in/ada"
    assert rows[0].github == "github.com/ada"


def test_second_submission_with_blank_fields_nulls_out_previous_values(
    client: TestClient, session: Session
):
    # Documents the intentional trade-off from ADR-0002: the upsert itself
    # does not guard against blank fields, only the pre-filled /form does.
    client.post("/info", data=_info_payload(), follow_redirects=False)

    response = client.post(
        "/info",
        data=_info_payload(first_name="", last_name="", email="", phone="",
                            location="", linkedin="", github=""),
        follow_redirects=False,
    )

    assert response.status_code == 303
    rows = session.exec(select(Info)).all()
    assert len(rows) == 1
    assert rows[0].first_name is None
    assert rows[0].email is None


def test_delete_for_nonexistent_id_returns_404_not_a_crash(client: TestClient):
    response = client.post("/info/999/delete", follow_redirects=False)

    assert response.status_code == 404


def test_delete_removes_the_row_and_redirects_to_manage(
    client: TestClient, session: Session
):
    client.post("/info", data=_info_payload(), follow_redirects=False)
    info_id = session.exec(select(Info)).all()[0].id

    response = client.post(f"/info/{info_id}/delete", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/manage"
    assert session.exec(select(Info)).all() == []


def test_form_prefills_with_existing_info_values_after_save(client: TestClient):
    client.post("/info", data=_info_payload(), follow_redirects=False)

    response = client.get("/form")

    assert response.status_code == 200
    assert 'value="Ada"' in response.text
    assert 'value="Lovelace"' in response.text
    assert 'value="ada@example.com"' in response.text
    assert 'value="555-0100"' in response.text
    assert 'value="London"' in response.text
    assert 'value="linkedin.com/in/ada"' in response.text
    assert 'value="github.com/ada"' in response.text
