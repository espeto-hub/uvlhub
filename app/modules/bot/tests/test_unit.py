import pytest

from app import apprise, db
from app.modules.auth.models import User
from app.modules.bot.models import Bot
from app.modules.conftest import faker as fk
from app.modules.conftest import login, logout
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def bot_generator(faker):
    def random_valid_bot(user, name=None, service_name=None, service_url=None, enabled=None, on_download_dataset=None,
                         on_download_file=None):

        while True:
            sn = service_name
            su = service_url
            if sn is None:
                sn = faker.random_element(apprise.service_names)
            if su is None:
                su = apprise.generate_url_example(sn)
            if su is not None:
                service_name = sn
                service_url = su
                break

        bot = Bot(
            name=faker.pystr(min_chars=3, max_chars=50) if name is None else name,
            service_name=service_name,
            service_url=service_url,
            user=user,
            enabled=faker.boolean() if enabled is None else enabled,
            on_download_dataset=faker.boolean() if on_download_dataset is None else on_download_dataset,
            on_download_file=faker.boolean() if on_download_file is None else on_download_file
        )
        return bot

    return random_valid_bot


@pytest.fixture(scope="module")
def user_generator(faker):
    def random_valid_user(email=None, password=None, name=None, surname=None):
        email = faker.email() if email is None else email
        password = faker.password() if password is None else password
        user = User(email=email, password=password)

        return user, password

    return random_valid_user


@pytest.fixture(scope="module")
def profile_generator(faker):
    def random_valid_profile(user, name=None, surname=None):
        profile = UserProfile(
            name=faker.first_name() if name is None else name,
            surname=faker.last_name() if surname is None else surname,
            user_id=user.id
        )
        return profile

    return random_valid_profile


@pytest.fixture(scope="class")
def users(request, faker, user_generator, profile_generator):
    if hasattr(request, "param"):
        request = request.param

        users = []

        for i in range(request):
            user, password = user_generator()
            db.session.add(user)
            db.session.commit()
            profile = profile_generator(user)
            db.session.add(profile)
            db.session.commit()
            users.append([user, profile, password])

        yield users

        for user, profile, _ in users:
            db.session.delete(profile)
            db.session.delete(user)
        db.session.commit()
    else:
        yield None


@pytest.fixture(scope="class")
def users_with_bots(request, users, bot_generator):
    if hasattr(request, "param"):
        request = request.param

        for user_details in users:
            user, _, _ = user_details
            user_details.append([])
            for i in range(request):
                bot = bot_generator(user)
                db.session.add(bot)
                user_details[3].append(bot)
        db.session.commit()

        yield users

        for i, user in enumerate(users):
            _, _, _, bots = user
            for bot in bots:
                db.session.delete(bot)
            user.remove(bots)
        db.session.commit()
    else:
        yield None


@pytest.fixture(scope="class")
def logged_in_client(request, test_client, users):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    user_index = request.param
    user = users[user_index][0]
    password = users[user_index][2]
    login(test_client, user.email, password)
    response = test_client.get("/profile/summary")

    assert response.status_code == 200
    assert b"User profile" in response.data

    yield test_client

    logout(test_client)


@pytest.mark.parametrize("users", [3], indirect=True)
class TestBotList:
    @pytest.fixture(scope="class")
    def test_client(self, test_client, faker, bot_generator, users):
        bots = []

        for i, user in enumerate(users):
            for j in range(i):
                bot = bot_generator(user[0], name=f"Bot {j + 1}")
                db.session.add(bot)
                bots.append(bot)
        db.session.commit()

        yield test_client

        for bot in bots:
            db.session.delete(bot)
        db.session.commit()

    def test_list_not_logged_in(self, test_client):
        response = test_client.get("/bots/list")
        assert response.status_code == 302
        assert response.headers["Location"] == "/login?next=%2Fbots%2Flist"

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_list_empty(self, logged_in_client, users):
        response = logged_in_client.get("/bots/list")

        assert response.status_code == 200
        assert b"You have no bots registered." in response.data

    @pytest.mark.parametrize("logged_in_client", [1], indirect=True)
    def test_list_one_bot(self, logged_in_client, users):
        response = logged_in_client.get("/bots/list")

        assert response.status_code == 200
        assert b"<table" in response.data
        assert response.data.count(b"<tr>") == 2
        assert b"Bot 1" in response.data

    @pytest.mark.parametrize("logged_in_client", [2], indirect=True)
    def test_list_many_bots(self, logged_in_client, users):
        response = logged_in_client.get("/bots/list")

        assert response.status_code == 200
        assert b"<table" in response.data
        assert response.data.count(b"<tr>") == 3
        for i in range(2):
            assert f"Bot {i + 1}".encode() in response.data


@pytest.mark.parametrize("users", [1], indirect=True)
class TestBotCreate:
    def test_create_not_logged_in(self, test_client, users):
        response = test_client.get("/bots/create")
        assert response.status_code == 302
        assert response.headers["Location"] == "/login?next=%2Fbots%2Fcreate"

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_create_get(self, logged_in_client, users):
        response = logged_in_client.get("/bots/create")

        assert response.status_code == 200
        assert b"Create bot" in response.data

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_create_post_empty(self, logged_in_client):
        response = logged_in_client.post("/bots/create", data={})

        assert response.status_code == 200
        assert b"Create bot" in response.data
        assert b"Please input a name" in response.data
        assert b"Please select a service" in response.data
        assert b"Please input an URL" in response.data

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_create_post_valid(self, logged_in_client, users, bot_generator):
        bot = bot_generator(users[0][0])
        response = logged_in_client.post(
            "/bots/create",
            data={
                'name': bot.name,
                'service_name': bot.service_name,
                'service_url': bot.service_url,
                'enabled': str(bot.enabled).lower(),
                'on_download_dataset': str(bot.on_download_dataset).lower(),
                'on_download_file': str(bot.on_download_file).lower(),
                'user_id': users[0][0].id,
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b"Bot created successfully" in response.data
        assert db.session.query(Bot).filter_by(user_id=users[0][0].id).count() == 1
        assert db.session.query(Bot).filter_by(user_id=users[0][0].id).first().name == bot.name

        db.session.query(Bot).filter_by(user_id=users[0][0].id).delete()

    invalid_bot = [
        pytest.param(
            {"name": ""},
            b"Please input a name.",
            id="name_empty",
        ),
        pytest.param(
            {"name": fk.pystr(max_chars=2)},
            b"Field must be between 3 and 50 characters long.",
            id="name_too_short",
        ),
        pytest.param(
            {"name": fk.pystr(min_chars=51, max_chars=55)},
            b"Field must be between 3 and 50 characters long.",
            id="name_too_long",
        ),
        pytest.param(
            {"service_name": "", "service_url": ""},
            b"Please select a service",
            id="service_name_not_selected",
        ),
        pytest.param(
            {"service_name": "Select one...", "service_url": ""},
            b"Please select a service",
            id="service_name_not_selected",
        ),
        pytest.param(
            {"service_name": fk.pystr(), "service_url": ""},
            b"Not a valid choice",
            id="service_name_not_a_choice",
        ),
        pytest.param(
            {"service_url": ""},
            b"Please input an URL.",
            id="service_url_empty",
        ),
        pytest.param(
            {"service_url": fk.pystr()},
            b"URL does not match any template",
            id="service_url_random",
        ),
    ]

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    @pytest.mark.parametrize("bot_kwargs,error_message", invalid_bot)
    def test_create_post_invalid(self, logged_in_client, users, bot_generator, bot_kwargs, error_message):
        bot = bot_generator(users[0][0], **bot_kwargs)
        response = logged_in_client.post(
            "/bots/create",
            data={
                'name': bot.name,
                'service_name': bot.service_name,
                'service_url': bot.service_url,
                'enabled': str(bot.enabled).lower(),
                'on_download_dataset': str(bot.on_download_dataset).lower(),
                'on_download_file': str(bot.on_download_file).lower(),
                'user_id': users[0][0].id,
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert error_message in response.data
        assert db.session.query(Bot).filter_by(user_id=users[0][0].id).count() == 0

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_create_post_existing_name(self, logged_in_client, users, bot_generator):
        bot = bot_generator(users[0][0])
        db.session.add(bot)
        db.session.commit()

        response = logged_in_client.post(
            "/bots/create",
            data={
                'name': bot.name,
                'service_name': bot.service_name,
                'service_url': bot.service_url,
                'enabled': str(bot.enabled).lower(),
                'on_download_dataset': str(bot.on_download_dataset).lower(),
                'on_download_file': str(bot.on_download_file).lower(),
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b"This name is already in use" in response.data
        assert db.session.query(Bot).filter_by(user_id=users[0][0].id).count() == 1

        db.session.query(Bot).filter_by(user_id=users[0][0].id).delete()

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_create_post_not_tested(self, logged_in_client, users, bot_generator):
        bot = bot_generator(users[0][0])
        response = logged_in_client.post(
            "/bots/create",
            data={
                'name': bot.name,
                'service_name': bot.service_name,
                'service_url': bot.service_url,
                'enabled': str(bot.enabled).lower(),
                'on_download_dataset': str(bot.on_download_dataset).lower(),
                'on_download_file': str(bot.on_download_file).lower(),
                'user_id': users[0][0].id,
                'is_tested': 'false',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b"Please test the bot first" in response.data
        assert db.session.query(Bot).filter_by(user_id=users[0][0].id).count() == 0


@pytest.mark.parametrize("users", [2], indirect=True)
@pytest.mark.parametrize("users_with_bots", [2], indirect=True)
class TestBotEdit:
    def test_edit_not_logged_in(self, test_client, users_with_bots):
        response = test_client.get("/bots/edit/1")
        assert response.status_code == 302
        assert response.headers["Location"] == "/login?next=%2Fbots%2Fedit%2F1"

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_edit_get_mine(self, logged_in_client, users_with_bots):
        for bot in users_with_bots[0][3]:
            response = logged_in_client.get(f"/bots/edit/{bot.id}")

            assert response.status_code == 200
            assert b"Edit bot" in response.data
            assert bot.name.encode() in response.data

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_edit_get_others(self, logged_in_client, users_with_bots):
        for user_with_bot in users_with_bots[1:]:
            for bot in user_with_bot[3]:
                response = logged_in_client.get(f"/bots/edit/{bot.id}")

                assert response.status_code == 403

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_edit_get_empty(self, logged_in_client, users_with_bots):
        response = logged_in_client.get("/bots/edit")

        assert response.status_code == 404

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_edit_get_invalid(self, logged_in_client, users_with_bots):
        response = logged_in_client.get("/bots/edit/" + fk.pystr(max_chars=5))

        assert response.status_code == 404

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_edit_post_empty(self, logged_in_client, users_with_bots):
        for bot in users_with_bots[0][3]:
            response = logged_in_client.post(f"/bots/edit/{bot.id}", data={
                'name': '',
                'service_name': '',
                'service_url': '',
                'enabled': '',
                'on_download_dataset': '',
                'on_download_file': '',
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            })

            assert response.status_code == 200
            assert b"Edit bot" in response.data
            assert b"Please input a name" in response.data
            assert b"Please select a service" in response.data
            assert b"Please input an URL" in response.data

    valid_bots = [
        pytest.param(
            {"name": fk.pystr(min_chars=3, max_chars=50)},
            id="edit_name",
        ),
        pytest.param(
            {
                "service_name": "Discord",
                "service_url": "discord://1234567890/abcdef",
            },
            id="edit_service_name_and_url",
        ),
    ]

    @pytest.mark.parametrize("logged_in_client", [1], indirect=True)
    @pytest.mark.parametrize("bot_kwargs", valid_bots)
    def test_edit_post_valid(self, logged_in_client, users_with_bots, bot_kwargs):
        bot = fk.random_element(users_with_bots[1][3])
        response = logged_in_client.post(
            f"/bots/edit/{bot.id}",
            data=bot_kwargs | {
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Bot edited successfully" in response.data
        for key, value in bot_kwargs.items():
            assert str(getattr(db.session.query(Bot).get(bot.id), key)) == value

    invalid_bots = [
        pytest.param(
            {"name": ""},
            b"Please input a name.",
            id="edit_name_empty",
        ),
        pytest.param(
            {"name": fk.pystr(max_chars=2)},
            b"Field must be between 3 and 50 characters long.",
            id="edit_name_too_short",
        ),
        pytest.param(
            {"name": fk.pystr(min_chars=51, max_chars=55)},
            b"Field must be between 3 and 50 characters long.",
            id="edit_name_too_long",
        ),
        pytest.param(
            {"service_name": "", "service_url": ""},
            b"Please select a service",
            id="edit_service_name_not_selected",
        ),
        pytest.param(
            {"service_name": "Select one...", "service_url": ""},
            b"Please select a service",
            id="edit_service_name_not_selected",
        ),
        pytest.param(
            {"service_name": fk.pystr(), "service_url": ""},
            b"Not a valid choice",
            id="edit_service_name_not_a_choice",
        ),
        pytest.param(
            {"service_url": ""},
            b"Please input an URL.",
            id="edit_service_url_empty",
        ),
        pytest.param(
            {"service_url": fk.pystr()},
            b"URL does not match any template",
            id="edit_service_url_random",
        ),
    ]

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    @pytest.mark.parametrize("bot_kwargs,error_message", invalid_bots)
    def test_edit_post_invalid(self, logged_in_client, users_with_bots, bot_kwargs, error_message):
        bot = fk.random_element(users_with_bots[0][3])
        response = logged_in_client.post(
            f"/bots/edit/{bot.id}",
            data=bot_kwargs | {
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert error_message in response.data
        for key, value in bot_kwargs.items():
            assert str(getattr(db.session.query(Bot).get(bot.id), key)) != value

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_edit_post_existing_name(self, logged_in_client, users_with_bots):
        bot = users_with_bots[0][3][0]
        other_bot = users_with_bots[0][3][1]
        response = logged_in_client.post(
            f"/bots/edit/{bot.id}",
            data={
                'name': other_bot.name,
                'service_name': bot.service_name,
                'service_url': bot.service_url,
                'enabled': str(bot.enabled).lower(),
                'on_download_dataset': str(bot.on_download_dataset).lower(),
                'on_download_file': str(bot.on_download_file).lower(),
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b"This name is already in use" in response.data
        assert db.session.query(Bot).filter_by(name=bot.name).count() == 1

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_edit_post_not_tested(self, logged_in_client, users_with_bots):
        bot = users_with_bots[0][3][0]
        new_name = fk.pystr(min_chars=3, max_chars=50)
        response = logged_in_client.post(
            f"/bots/edit/{bot.id}",
            data={
                'name': new_name,
                'service_name': bot.service_name,
                'service_url': bot.service_url,
                'enabled': str(bot.enabled).lower(),
                'on_download_dataset': str(bot.on_download_dataset).lower(),
                'on_download_file': str(bot.on_download_file).lower(),
                'is_tested': 'false',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b"Please test the bot first" in response.data
        assert db.session.query(Bot).get(bot.id).name != new_name
