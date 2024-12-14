import pytest
from flask import Flask
from app.modules.fakenodo import fakenodo_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(fakenodo_bp)
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def test_test_fakenodo_connection(client):
    response = client.get("/fakenodo/api")
    assert response.status_code == 200
    assert response.json == {"status": "success", "message": "You have successfully connected to Fakenodo"}


def test_create_deposition(client):
    response = client.post("/fakenodo/api")
    assert response.status_code == 201
    assert response.json == {"status": "success", "message": "You have successfully created a deposition in Fakenodo"}


def test_create_deposition_files(client):
    deposition_id = 123
    response = client.post(f"/fakenodo/api/{deposition_id}/files")
    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "message": "You have successfuly uploaded deposition files in Fakenodo.",
    }


def test_delete_deposition(client):
    deposition_id = 123
    response = client.delete(f"/fakenodo/api/{deposition_id}")
    assert response.status_code == 200
    assert response.json == {"status": "success", "message": "You hace successfully deleted a deposition in Fakenodo"}


def test_publish_deposition(client):
    deposition_id = 123
    response = client.post(f"/fakenodo/api/{deposition_id}/actions/publish")
    assert response.status_code == 202
    assert response.json == {"status": "success", "message": "You have successfully published a deposition in Fakenodo"}


def test_get_deposition(client):
    deposition_id = 123
    response = client.get(f"/fakenodo/api/{deposition_id}")
    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "message": "You have successfully retrieved a deposition in Fakenodo",
        "doi": "10.1234/fakenodo.123456",

    }
