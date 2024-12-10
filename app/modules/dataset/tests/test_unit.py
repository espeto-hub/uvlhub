import pytest
from flask import url_for
from app import create_app, db
from app.modules.dataset.models import DataSet, Rating
from app.modules.auth.models import User
from flask_login import login_user


@pytest.fixture
def test_client():
    """Fixture para el cliente de pruebas."""
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            # Limpiar y crear la base de datos
            db.drop_all()
            db.create_all()

            # Crear un usuario de prueba
            user = User(email="test@example.com", password="password123")
            db.session.add(user)
            db.session.commit()

            # Crear un dataset de prueba
            dataset = DataSet(name="Test Dataset", user_id=user.id)
            db.session.add(dataset)
            db.session.commit()

            # Iniciar sesión como el usuario de prueba
            login_user(user)

            yield client

            db.session.remove()
            db.drop_all()


def test_rate_dataset_get(test_client):
    """Test para la solicitud GET de la ruta de calificación del dataset."""
    # Obtener el dataset creado en el fixture
    dataset = DataSet.query.first()

    # Realizar la solicitud GET
    response = test_client.get(url_for('dataset.rate_dataset', dataset_id=dataset.id))

    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    assert b'Calificacion' in response.data  # Verificar que el formulario esté presente en la página


def test_rate_dataset_post(test_client):
    """Test para la solicitud POST de la ruta de calificación del dataset."""
    dataset = DataSet.query.first()

    # Datos del formulario (calificación de 5)
    form_data = {
        'score': 5  # Calificación de 5
    }

    # Realizar la solicitud POST con los datos del formulario
    response = test_client.post(url_for('dataset.rate_dataset', dataset_id=dataset.id), data=form_data, 
                                follow_redirects=True)

    # Verificar que la respuesta sea una redirección a la vista del dataset
    assert response.status_code == 200
    assert b'Vista del Dataset' in response.data  # Asegurarnos de que la vista del dataset se muestre tras la redirección

    # Verificar que la calificación se haya guardado en la base de datos
    rating = Rating.query.filter_by(dataset_id=dataset.id).first()
    assert rating is not None
    assert rating.score == 5  # Verificar que la calificación sea la esperada
    assert rating.user_id == 1  # Asegurarse de que el usuario de la calificación sea el correcto


def test_rate_dataset_post_with_invalid_data(test_client):
    """Test para la solicitud POST con datos inválidos."""
    dataset = DataSet.query.first()

    # Datos del formulario inválidos (por ejemplo, sin calificación)
    form_data = {
        'score': None  # Calificación inválida
    }

    # Realizar la solicitud POST con los datos inválidos
    response = test_client.post(url_for('dataset.rate_dataset', dataset_id=dataset.id), data=form_data, 
                                follow_redirects=True)

    # Verificar que se muestra un mensaje de error
    assert response.status_code == 200
    assert b'Hubo un problema al guardar la calificacion' in response.data  # Verificar el mensaje de error


def test_rate_dataset_redirect_on_success(test_client):
    """Test para asegurarse de que la calificación se guarda y redirige correctamente."""
    dataset = DataSet.query.first()

    # Datos del formulario válidos
    form_data = {
        'score': 4  # Calificación válida
    }

    # Realizar la solicitud POST con los datos válidos
    response = test_client.post(url_for('dataset.rate_dataset', dataset_id=dataset.id), data=form_data, 
                                follow_redirects=True)

    # Verificar la redirección al detalle del dataset
    assert response.status_code == 200
    assert b'Vista del Dataset' in response.data

    # Verificar que la calificación se haya guardado correctamente
    rating = Rating.query.filter_by(dataset_id=dataset.id).first()
    assert rating is not None
    assert rating.score == 4  # Verificar que la calificación guardada sea la esperada
