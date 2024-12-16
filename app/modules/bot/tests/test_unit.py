import os
import shutil
from datetime import datetime, timezone
from unittest.mock import patch
from urllib.parse import quote

import pytest
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

from app import apprise, db
from app.modules.auth.models import User
from app.modules.bot.models import Bot
from app.modules.conftest import faker as fk
from app.modules.conftest import login, logout
from app.modules.dataset.models import DSMetrics, DSMetaData, PublicationType, Author, DataSet, DSDownloadRecord
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from app.modules.hubfile.models import Hubfile, HubfileDownloadRecord
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def bot_generator(faker):
    def random_valid_bot(
        user,
        name=None,
        service_name=None,
        service_url=None,
        enabled=None,
        on_download_dataset=None,
        on_download_file=None,
        url_template=None,
    ):

        if service_name is None:
            service_name = faker.random_element(apprise.service_names)
        if service_url is None:
            service_url = apprise.generate_url_example(service_name, url_template)

        bot = Bot(
            name=faker.pystr(min_chars=3, max_chars=50) if name is None else name,
            service_name=service_name,
            service_url=service_url,
            user=user,
            enabled=faker.boolean() if enabled is None else enabled,
            on_download_dataset=faker.boolean() if on_download_dataset is None else on_download_dataset,
            on_download_file=faker.boolean() if on_download_file is None else on_download_file,
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
            user_id=user.id,
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
    @pytest.mark.parametrize(
        "service_name,url_template", [(s, t) for s in apprise.service_names for t in apprise.get_service_templates(s)]
    )
    def test_create_post_valid(self, logged_in_client, users, bot_generator, service_name, url_template):
        bot = bot_generator(users[0][0], service_name=service_name, url_template=url_template)
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
            follow_redirects=True,
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
            follow_redirects=True,
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
            follow_redirects=True,
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
            follow_redirects=True,
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
            response = logged_in_client.post(
                f"/bots/edit/{bot.id}",
                data={
                    'name': '',
                    'service_name': '',
                    'service_url': '',
                    'enabled': '',
                    'on_download_dataset': '',
                    'on_download_file': '',
                    'is_tested': 'true',
                    'test': 'false',
                    'submit': 'true',
                },
            )

            assert response.status_code == 200
            assert b"Edit bot" in response.data
            assert b"Please input a name" in response.data
            assert b"Please select a service" in response.data
            assert b"Please input an URL" in response.data

    @pytest.mark.parametrize("logged_in_client", [1], indirect=True)
    def test_edit_post_valid_name(self, logged_in_client, users_with_bots):
        bot = fk.random_element(users_with_bots[1][3])
        new_name = bot.name
        while new_name == bot.name:
            new_name = fk.pystr(min_chars=3, max_chars=50)
        response = logged_in_client.post(
            f"/bots/edit/{bot.id}",
            data={
                'name': new_name,
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Bot edited successfully" in response.data
        assert db.session.query(Bot).get(bot.id).name == new_name

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    @pytest.mark.parametrize(
        "service_name,url_template", [(s, t) for s in apprise.service_names for t in apprise.get_service_templates(s)]
    )
    def test_edit_post_valid_service_and_url(self, logged_in_client, users_with_bots, service_name, url_template):
        bot = fk.random_element(users_with_bots[0][3])
        new_service_name = service_name
        new_service_url = apprise.generate_url_example(service_name, url_template)
        response = logged_in_client.post(
            f"/bots/edit/{bot.id}",
            data={
                'name': bot.name,
                'service_name': new_service_name,
                'service_url': new_service_url,
                'enabled': str(bot.enabled).lower(),
                'on_download_dataset': str(bot.on_download_dataset).lower(),
                'on_download_file': str(bot.on_download_file).lower(),
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Bot edited successfully" in response.data
        assert db.session.query(Bot).get(bot.id).service_name == new_service_name
        assert db.session.query(Bot).get(bot.id).service_url == new_service_url

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
            data=bot_kwargs
            | {
                'is_tested': 'true',
                'test': 'false',
                'submit': 'true',
            },
            follow_redirects=True,
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
            follow_redirects=True,
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
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Please test the bot first" in response.data
        assert db.session.query(Bot).get(bot.id).name != new_name


@pytest.mark.parametrize("users", [2], indirect=True)
@pytest.mark.parametrize("users_with_bots", [2], indirect=True)
class TestBotDelete:
    def test_delete_post_not_logged_in(self, test_client, users_with_bots):
        response = test_client.post("/bots/delete/1")
        assert response.status_code == 302
        assert response.headers["Location"] == "/login?next=%2Fbots%2Fdelete%2F1"

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_delete_post_mine(self, logged_in_client, users_with_bots):
        for bot in users_with_bots[0][3]:
            response = logged_in_client.post(f"/bots/delete/{bot.id}")

            assert response.status_code == 302
            assert response.headers["Location"] == "/bots/list"

        response = logged_in_client.get("/bots/list")
        assert response.status_code == 200
        assert b"You have no bots registered." in response.data
        assert db.session.query(Bot).filter_by(user_id=users_with_bots[0][0].id).count() == 0

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_delete_post_others(self, logged_in_client, users_with_bots):
        for user_with_bot in users_with_bots[1:]:
            for bot in user_with_bot[3]:
                response = logged_in_client.post(f"/bots/delete/{bot.id}")

                assert response.status_code == 403

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_delete_post_empty(self, logged_in_client, users_with_bots):
        response = logged_in_client.get("/bots/delete")

        assert response.status_code == 404

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_delete_post_invalid(self, logged_in_client, users_with_bots):
        response = logged_in_client.get("/bots/delete/" + fk.pystr(max_chars=5))

        assert response.status_code == 404


@pytest.mark.parametrize("users", [1], indirect=True)
class TestBotGuide:
    @pytest.mark.parametrize("service_name", apprise.service_names)
    def test_guide_not_logged_in(self, test_client, users, service_name):
        service_name_quoted = quote(service_name.replace('/', '|'))
        response = test_client.get(f"/bots/guide/{service_name_quoted}")
        assert response.status_code == 302
        assert "/login?next=%2Fbots%2Fguide%2F" in response.headers["Location"]

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    @pytest.mark.parametrize("service_name", apprise.service_names)
    def test_guide_get(self, logged_in_client, users, service_name):
        service_name_quoted = quote(service_name.replace('/', '|'))
        response = logged_in_client.get(f"/bots/guide/{service_name_quoted}")

        assert response.status_code == 200
        if b"has no documentation available" not in response.data:
            assert service_name.encode() in response.data
            assert b'<h2>Templates</h2>' in response.data
            assert b'<h2>Tokens</h2>' in response.data
            assert b'<h2>Examples</h2>' in response.data
            assert b'<h2>Information</h2>' in response.data

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_guide_get_empty(self, logged_in_client, users):
        response = logged_in_client.get("/bots/guide")

        assert response.status_code == 404

    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_guide_get_invalid(self, logged_in_client, users):
        response = logged_in_client.get("/bots/guide/" + quote(fk.pystr(max_chars=5), safe=''))

        assert response.status_code == 404


@pytest.mark.parametrize("users", [2], indirect=True)
@pytest.mark.parametrize("users_with_bots", [1], indirect=True)
class TestBotMessaging:
    def seed(self, db, data):
        if not data:
            return []

        model = type(data[0])
        if not all(isinstance(obj, model) for obj in data):
            raise ValueError("All objects must be of the same model.")

        try:
            db.session.add_all(data)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise Exception(f"Failed to insert data into `{model.__tablename__}` table. Error: {e}")

        # After committing, the `data` objects should have their IDs assigned.
        return data

    @pytest.fixture(scope="class")
    def test_client(self, test_client, users_with_bots):
        user1 = users_with_bots[0][0]
        user2 = users_with_bots[1][0]

        ds_metrics = DSMetrics(number_of_models='5', number_of_features='50')
        seeded_ds_metrics = self.seed(db, [ds_metrics])[0]

        ds_meta_data_list = [
            DSMetaData(
                deposition_id=1 + i,
                title=f'Sample dataset {i + 1}',
                description=f'Description for dataset {i + 1}',
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
                publication_doi=f'10.1234/dataset{i + 1}',
                dataset_doi=f'10.1234/dataset{i + 1}',
                tags='tag1, tag2',
                ds_metrics_id=seeded_ds_metrics.id,
            )
            for i in range(4)
        ]
        seeded_ds_meta_data = self.seed(db, ds_meta_data_list)

        authors = [
            Author(
                name=f'Author {i + 1}',
                affiliation=f'Affiliation {i + 1}',
                orcid=f'0000-0000-0000-000{i}',
                ds_meta_data_id=seeded_ds_meta_data[i % 4].id,
            )
            for i in range(4)
        ]
        self.seed(db, authors)

        datasets = [
            DataSet(
                user_id=user1.id if i % 2 == 0 else user2.id,
                ds_meta_data_id=seeded_ds_meta_data[i].id,
                created_at=datetime.now(timezone.utc),
            )
            for i in range(4)
        ]
        seeded_datasets = self.seed(db, datasets)

        fm_meta_data_list = [
            FMMetaData(
                uvl_filename=f'file{i + 1}.uvl',
                title=f'Feature Model {i + 1}',
                description=f'Description for feature model {i + 1}',
                publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
                publication_doi=f'10.1234/fm{i + 1}',
                tags='tag1, tag2',
                uvl_version='1.0',
            )
            for i in range(12)
        ]
        seeded_fm_meta_data = self.seed(db, fm_meta_data_list)

        fm_authors = [
            Author(
                name=f'Author {i + 5}',
                affiliation=f'Affiliation {i + 5}',
                orcid=f'0000-0000-0000-000{i + 5}',
                fm_meta_data_id=seeded_fm_meta_data[i].id,
            )
            for i in range(12)
        ]
        self.seed(db, fm_authors)

        feature_models = [
            FeatureModel(data_set_id=seeded_datasets[i // 3].id, fm_meta_data_id=seeded_fm_meta_data[i].id)
            for i in range(12)
        ]
        seeded_feature_models = self.seed(db, feature_models)

        load_dotenv()
        working_dir = os.getenv('WORKING_DIR', '')
        src_folder = os.path.join(working_dir, 'app', 'modules', 'dataset', 'uvl_examples')
        seeded_files = []
        for i in range(12):
            file_name = f'file{i + 1}.uvl'
            feature_model = seeded_feature_models[i]
            dataset = next(ds for ds in seeded_datasets if ds.id == feature_model.data_set_id)
            user_id = dataset.user_id

            dest_folder = os.path.join(working_dir, 'uploads', f'user_{user_id}', f'dataset_{dataset.id}')
            os.makedirs(dest_folder, exist_ok=True)
            shutil.copy(os.path.join(src_folder, file_name), dest_folder)

            file_path = os.path.join(dest_folder, file_name)

            uvl_file = Hubfile(
                name=file_name,
                checksum=f'checksum{i + 1}',
                size=os.path.getsize(file_path),
                feature_model_id=feature_model.id,
            )
            seeded_files.append(self.seed(db, [uvl_file]))

        yield test_client

        # Delete all objects in DSDownloadRecord
        db.session.query(DSDownloadRecord).delete()
        db.session.query(HubfileDownloadRecord).delete()

    @patch("app.apprise.send_test_message")
    @pytest.mark.parametrize("logged_in_client", [0], indirect=True)
    def test_messaging_test_message(self, mock_send_test_message, logged_in_client, users_with_bots):
        mock_send_test_message.return_value = True, ""

        bot = users_with_bots[0][3][0]
        new_service_name = fk.random_element(apprise.service_names)
        new_service_url = apprise.generate_url_example(new_service_name)

        response = logged_in_client.post(
            f"/bots/edit/{bot.id}",
            data={
                'service_name': new_service_name,
                'service_url': new_service_url,
                'test': 'true',
                'submit': 'false',
            },
        )

        assert response.status_code == 200
        assert '✔'.encode() in response.data

        mock_send_test_message.assert_called_once()
        assert mock_send_test_message.call_args[0][0] == new_service_url
        assert db.session.query(Bot).get(bot.id).service_name == bot.service_name
        assert db.session.query(Bot).get(bot.id).service_url == bot.service_url

    @patch("app.apprise.send_message")
    @pytest.mark.parametrize("logged_in_client", [1], indirect=True)
    @pytest.mark.parametrize("enabled", [True, False], ids=["enabled", "disabled"])
    @pytest.mark.parametrize(
        "on_download_dataset", [True, False], ids=["on_download_dataset", "not_on_download_dataset"]
    )
    def test_messaging_on_download_dataset(
        self, mock_send_message, logged_in_client, users_with_bots, enabled, on_download_dataset
    ):
        uploader = users_with_bots[0][0]
        bot = users_with_bots[0][3][0]
        dataset = fk.random_element([ds for ds in DataSet.query.filter_by(user_id=uploader.id).all()])

        mock_send_message.return_value = True

        bot.enabled = enabled
        bot.on_download_dataset = on_download_dataset
        db.session.commit()

        assert db.session.query(Bot).get(bot.id).enabled == enabled
        assert db.session.query(Bot).get(bot.id).on_download_dataset == on_download_dataset

        response = logged_in_client.get(f"/dataset/download/{dataset.id}")

        assert response.status_code == 200
        if enabled and on_download_dataset:
            mock_send_message.assert_called_once()
            assert bot.service_url in mock_send_message.call_args[0][0]
        else:
            mock_send_message.assert_called_once()
            assert mock_send_message.call_args[0][0] == []

    @patch("app.apprise.send_message")
    @pytest.mark.parametrize("logged_in_client", [1], indirect=True)
    @pytest.mark.parametrize("enabled", [True, False], ids=["enabled", "disabled"])
    @pytest.mark.parametrize("on_download_file", [True, False], ids=["on_download_file", "not_on_download_file"])
    @pytest.mark.parametrize(
        "route,content_type,extension",
        [
            ("/file/download", "application/octet-stream", '.uvl'),
            ("/flamapy/to_glencoe", "text/plain; charset=utf-8", ".uvl_glencoe.txt"),
            ("/flamapy/to_splot", "text/plain; charset=utf-8", '.uvl_splot.txt'),
            ("/flamapy/to_cnf", "text/plain; charset=utf-8", '.uvl_cnf.txt'),
        ],
        ids=["uvl", "glencoe", "splot", "cnf"],
    )
    def test_messaging_on_download_file(
        self,
        mock_send_message,
        logged_in_client,
        users_with_bots,
        enabled,
        on_download_file,
        route,
        content_type,
        extension,
    ):
        uploader = users_with_bots[0][0]
        bot = users_with_bots[0][3][0]
        dataset = fk.random_element([ds for ds in DataSet.query.filter_by(user_id=uploader.id).all()])
        feature_model = fk.random_element([fm for fm in FeatureModel.query.filter_by(data_set_id=dataset.id).all()])
        file = fk.random_element([f for f in Hubfile.query.filter_by(feature_model_id=feature_model.id).all()])

        mock_send_message.return_value = True

        bot.enabled = enabled
        bot.on_download_file = on_download_file
        db.session.commit()

        assert db.session.query(Bot).get(bot.id).enabled == enabled
        assert db.session.query(Bot).get(bot.id).on_download_file == on_download_file

        response = logged_in_client.get(f"{route}/{file.id}", follow_redirects=True)

        assert response.status_code == 200
        assert response.content_type == content_type
        assert response.headers['Content-Disposition'].endswith(extension)
        if enabled and on_download_file:
            mock_send_message.assert_called_once()
            assert bot.service_url in mock_send_message.call_args[0][0]
        else:
            mock_send_message.assert_called_once()
            assert mock_send_message.call_args[0][0] == []
