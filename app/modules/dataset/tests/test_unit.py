import pytest
from flask import url_for
from app import create_app, db
from app.modules.dataset.models import DataSet, Rating, DSMetaData
from app.modules.auth.models import User
from flask_login import login_user
from app.modules.dataset.models import PublicationType


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

            # Crear un DSMETAData de prueba (asegúrate de tener el modelo correcto)
            ds_meta_data = DSMetaData(title="Test Metadata", description="Test Description", 
                                      publication_type=PublicationType.BOOK)
            db.session.add(ds_meta_data)
            db.session.commit()

            # Crear un dataset de prueba asociado al DSMETAData
            dataset = DataSet(name="Test Dataset", user_id=user.id, ds_meta_data_id=ds_meta_data.id)
            db.session.add(dataset)
            db.session.commit()

            # Iniciar sesión como el usuario de prueba
            login_user(user)

            yield client

            db.session.remove()
            db.drop_all()


def test_rate_dataset_get(test_client):
    """Test para la solicitud GET de la ruta de calificación del dataset."""
    dataset = DataSet.query.first()  # Debería obtenerse correctamente ya que hemos asociado DSMetaData

    # Realizar la solicitud GET
    response = test_client.get(url_for('dataset.rate_dataset', dataset_id=dataset.id))

    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200


def test_rate_dataset_post(test_client):
    """Test para la solicitud POST de la ruta de calificación del dataset."""
    dataset = DataSet.query.first()  # Debería ser un dataset con ds_meta_data_id

    # Datos del formulario (calificación de 5)
    form_data = {
        'score': 5  # Calificación de 5
    }

    # Realizar la solicitud POST con los datos del formulario
    response = test_client.post(url_for('dataset.rate_dataset', dataset_id=dataset.id), data=form_data,
                                follow_redirects=True)

    # Verificar que la respuesta sea una redirección a la vista del dataset
    assert response.status_code == 200
    assert b'Vista del Dataset' in response.data

    # Verificar que la calificación se haya guardado en la base de datos
    rating = Rating.query.filter_by(dataset_id=dataset.id).first()
    assert rating is not None
    assert rating.score == 5  # Verificar que la calificación sea la esperada
    assert rating.user_id == 1  # Asegurarse de que el usuario de la calificación sea el correcto