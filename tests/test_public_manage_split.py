"""Covers ticket #9: public `/` vs. management `/manage` routing split.

Per-entity Modifier/Supprimer coverage already lives in each entity's own
test module (test_education_update.py etc.); this module covers the
cross-cutting acceptance criteria that don't belong to any single entity.
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import Education, Info, Language, Project, ProfessionalExperience, Skill


def _seed_one_of_everything(session: Session) -> None:
    session.add(Info(first_name="Ada", last_name="Lovelace"))
    session.add(
        ProfessionalExperience(company="Acme", position="Engineer", start_date=2020)
    )
    session.add(Education(school="MIT", degree="BSc"))
    session.add(Skill(software="Python", level="Avancé"))
    session.add(Language(language_name="Français", level="Courant"))
    session.add(Project(name_project="CV Generator", description="A portfolio tool"))
    session.commit()


def test_public_portfolio_has_no_edit_or_delete_forms(
    client: TestClient, session: Session
):
    _seed_one_of_everything(session)

    response = client.get("/")

    assert response.status_code == 200
    assert "Modifier" not in response.text
    assert "Supprimer" not in response.text
    assert "/delete" not in response.text
    assert "/edit" not in response.text


def test_public_portfolio_has_visible_export_pdf_button(
    client: TestClient, session: Session
):
    _seed_one_of_everything(session)

    response = client.get("/")

    assert response.status_code == 200
    assert 'onclick="window.print()"' in response.text
    assert "Exporter en PDF" in response.text


def test_stylesheet_hides_export_and_manage_chrome_when_printing(client: TestClient):
    response = client.get("/static/style.css")

    assert response.status_code == 200
    assert "@media print" in response.text
    # The toolbar wraps both the export button and the /manage link, so
    # hiding it in print hides both pieces of non-portfolio chrome.
    print_block = response.text.split("@media print", 1)[1]
    assert ".pf-toolbar" in print_block


def test_public_portfolio_links_to_manage(client: TestClient, session: Session):
    _seed_one_of_everything(session)

    response = client.get("/")

    assert response.status_code == 200
    assert 'href="/manage"' in response.text


def test_manage_view_shows_every_entity_with_modifier_and_supprimer(
    client: TestClient, session: Session
):
    _seed_one_of_everything(session)

    response = client.get("/manage")
    text = response.text

    assert response.status_code == 200

    info = session.exec(select(Info)).all()[0]
    assert f"/info/{info.id}/delete" in text

    experience = session.exec(select(ProfessionalExperience)).all()[0]
    assert f"/professional_experience/{experience.id}/edit" in text
    assert f"/professional_experience/{experience.id}/delete" in text

    education = session.exec(select(Education)).all()[0]
    assert f"/education/{education.id}/edit" in text
    assert f"/education/{education.id}/delete" in text

    skill = session.exec(select(Skill)).all()[0]
    assert f"/skills/{skill.id}/edit" in text
    assert f"/skills/{skill.id}/delete" in text

    language = session.exec(select(Language)).all()[0]
    assert f"/languages/{language.id}/edit" in text
    assert f"/languages/{language.id}/delete" in text

    project = session.exec(select(Project)).all()[0]
    assert f"/projects/{project.id}/edit" in text
    assert f"/projects/{project.id}/delete" in text


def test_manage_view_has_no_export_pdf_button(client: TestClient, session: Session):
    _seed_one_of_everything(session)

    response = client.get("/manage")

    assert response.status_code == 200
    assert "Exporter en PDF" not in response.text


def test_create_actions_redirect_to_form(client: TestClient):
    assert client.post(
        "/skills", data={"software": "Rust"}, follow_redirects=False
    ).headers["location"] == "/form"
    assert client.post(
        "/education", data={"school": "MIT"}, follow_redirects=False
    ).headers["location"] == "/form"
    assert client.post(
        "/professional_experience",
        data={"company": "Acme"},
        follow_redirects=False,
    ).headers["location"] == "/form"
    assert client.post(
        "/languages", data={"language_name": "Anglais"}, follow_redirects=False
    ).headers["location"] == "/form"
    assert client.post(
        "/projects", data={"name_project": "Site"}, follow_redirects=False
    ).headers["location"] == "/form"
    assert client.post(
        "/info", data={"first_name": "Ada"}, follow_redirects=False
    ).headers["location"] == "/form"
