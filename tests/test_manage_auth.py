"""Covers ticket #10: HTTP Basic Auth protecting /manage and /form.

Per ADR-0003, every route under /manage and /form (edit forms, create,
update, delete) sits behind the same HTTP Basic Auth gate; `/` and its
rendering stay fully public. Credentials come from the ADMIN_USERNAME /
ADMIN_PASSWORD environment variables (set in conftest.py before `main` is
imported), never hardcoded.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from main import Education, Language, Project, ProfessionalExperience, Skill

WRONG_CREDENTIALS = ("someone-else", "not-the-password")


# Every GET route that should require auth, independent of any seeded data.
PROTECTED_GET_ROUTES = [
    "/manage",
    "/form",
]

# Every POST create route that should require auth (ADR-0003: /form and
# "every entity's create route, and /info").
PROTECTED_CREATE_ROUTES = [
    "/skills",
    "/education",
    "/professional_experience",
    "/languages",
    "/projects",
    "/info",
]


@pytest.mark.parametrize("path", PROTECTED_GET_ROUTES)
def test_get_without_credentials_returns_401_with_basic_challenge(
    client: TestClient, path: str
):
    response = client.get(path, auth=None)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


@pytest.mark.parametrize("path", PROTECTED_CREATE_ROUTES)
def test_create_route_without_credentials_returns_401_with_basic_challenge(
    client: TestClient, path: str
):
    response = client.post(path, data={}, auth=None)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


@pytest.mark.parametrize("path", PROTECTED_GET_ROUTES)
def test_get_with_incorrect_credentials_returns_401(client: TestClient, path: str):
    response = client.get(path, auth=WRONG_CREDENTIALS)

    assert response.status_code == 401


@pytest.mark.parametrize("path", PROTECTED_CREATE_ROUTES)
def test_create_route_with_incorrect_credentials_returns_401(
    client: TestClient, path: str
):
    response = client.post(path, data={}, auth=WRONG_CREDENTIALS)

    assert response.status_code == 401


@pytest.mark.parametrize("path", PROTECTED_GET_ROUTES)
def test_get_with_correct_credentials_succeeds(client: TestClient, path: str):
    # client's default auth (set in conftest.py) already holds the
    # correct credentials.
    response = client.get(path)

    assert response.status_code == 200


def test_create_route_with_correct_credentials_succeeds(client: TestClient):
    response = client.post(
        "/skills", data={"software": "Rust"}, follow_redirects=False
    )

    assert response.status_code == 303


def test_edit_and_update_and_delete_routes_require_auth(
    client: TestClient, session: Session
):
    experience = ProfessionalExperience(company="Acme", position="Engineer")
    education = Education(school="MIT", degree="BSc")
    skill = Skill(software="Python", level="Avancé")
    language = Language(language_name="Français", level="Courant")
    project = Project(name_project="CV Generator")
    session.add_all([experience, education, skill, language, project])
    session.commit()

    protected_edit_and_delete_calls = [
        ("get", f"/professional_experience/{experience.id}/edit"),
        ("post", f"/professional_experience/{experience.id}/update"),
        ("post", f"/professional_experience/{experience.id}/delete"),
        ("get", f"/education/{education.id}/edit"),
        ("post", f"/education/{education.id}/update"),
        ("post", f"/education/{education.id}/delete"),
        ("get", f"/skills/{skill.id}/edit"),
        ("post", f"/skills/{skill.id}/update"),
        ("post", f"/skills/{skill.id}/delete"),
        ("get", f"/languages/{language.id}/edit"),
        ("post", f"/languages/{language.id}/update"),
        ("post", f"/languages/{language.id}/delete"),
        ("get", f"/projects/{project.id}/edit"),
        ("post", f"/projects/{project.id}/update"),
        ("post", f"/projects/{project.id}/delete"),
        ("post", "/info/1/delete"),
    ]

    for method, path in protected_edit_and_delete_calls:
        response = getattr(client, method)(path, auth=None)
        assert response.status_code == 401, f"{method.upper()} {path}"
        assert response.headers["www-authenticate"] == "Basic"


def test_root_is_fully_accessible_without_credentials(client: TestClient):
    response = client.get("/", auth=None)

    assert response.status_code == 200
