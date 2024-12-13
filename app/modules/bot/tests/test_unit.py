import pytest

from app import db, apprise
from app.modules.auth.models import User
from app.modules.bot.models import Bot
from app.modules.conftest import login, logout
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def valid_bot_generator(faker):
    def random_valid_bot(user, name=None, service_name=None, service_url=None):
        while True:
            if service_name is None:
                service_name = faker.random_element(apprise.service_names)
            if service_url is None:
                service_url = apprise.generate_url_example(service_name)
            if service_url:
                break
        bot = Bot(
            name=faker.word() if name is None else name,
            service_name=service_name,
            service_url=service_url,
            user_id=user.id
        )
        return bot

    return random_valid_bot


class TestBotList:
    @pytest.fixture(scope="class")
    def test_client(self, test_client, faker, valid_bot_generator):
        """
        Extends the test_client fixture to add additional specific data for module testing.
        """
        with test_client.application.app_context():
            user_test = User(email='nobots@example.com', password='nobots')
            db.session.add(user_test)
            db.session.commit()

            profile = UserProfile(user_id=user_test.id, name="No", surname="Bots")
            db.session.add(profile)
            db.session.commit()

            user_test = User(email='onebot@example.com', password='onebot')
            db.session.add(user_test)
            db.session.commit()

            profile = UserProfile(user_id=user_test.id, name="One", surname="Bot")
            db.session.add(profile)
            db.session.commit()

            bot = valid_bot_generator(user_test, name="Bot 1")
            db.session.add(bot)
            db.session.commit()

            user_test = User(email='manybots@example.com', password='manybots')
            db.session.add(user_test)
            db.session.commit()

            profile = UserProfile(user_id=user_test.id, name="Many", surname="Bots")
            db.session.add(profile)
            db.session.commit()

            for i in range(3):
                bot = valid_bot_generator(user_test, name=f"Bot {i + 1}")
                db.session.add(bot)
            db.session.commit()

        yield test_client

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, test_client):
        """
        Setup method that runs before each test.
        """
        # Before

        yield

        # After
        logout(test_client)

    def test_list_not_logged_in(self, test_client):
        response = test_client.get("/bots/list")
        assert response.status_code == 302
        assert response.headers["Location"] == "/login?next=%2Fbots%2Flist"

    def test_list_empty(self, test_client):
        login_response = login(test_client, "nobots@example.com", "nobots")
        assert login_response.status_code == 200

        response = test_client.get("/bots/list")

        assert response.status_code == 200
        assert b"You have no bots registered." in response.data

    def test_list_one_bot(self, test_client):
        login_response = login(test_client, "onebot@example.com", "onebot")
        assert login_response.status_code == 200

        response = test_client.get("/bots/list")

        assert response.status_code == 200
        assert b"<table" in response.data
        assert response.data.count(b"<tr>") == 2
        assert b"Bot 1" in response.data

    def test_list_many_bots(self, test_client):
        login_response = login(test_client, "manybots@example.com", "manybots")
        assert login_response.status_code == 200

        response = test_client.get("/bots/list")

        assert response.status_code == 200
        assert b"<table" in response.data
        assert response.data.count(b"<tr>") == 4
        for i in range(3):
            assert f"Bot {i + 1}".encode() in response.data
