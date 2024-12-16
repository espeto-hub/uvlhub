import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_edit_profile_page_get(test_client):
    """
    Tests access to the profile editing page via a GET request.
    """
    login(test_client, "user@example.com", "test1234")

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."
    assert b"Edit profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_user_profile_page_get(test_client):
    """
    Tests access to some user profile that is logged int.
    """
    login(test_client, "user@example.com", "test1234")
    user = User.query.filter_by(email="user@example.com").first()

    url = f"/profile/{user.id}/"

    response = test_client.get(url)
    assert response.status_code == 200, f"The profile page for user {user.id} could not be accessed."

    logout(test_client)


def test_user_profile_no_log_in(test_client):
    """
    Tests access to some user profile that is logged int.
    """
    url = f"/profile/{1}/"

    response = test_client.get(url)
    assert response.status_code == 200, f"The profile page for user {1} could not be accessed."

    logout(test_client)
