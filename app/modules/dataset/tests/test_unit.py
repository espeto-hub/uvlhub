import pytest
from app import create_app, db
from flask_login import login_user
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.auth.models import User  # Asegúrate de que el modelo de usuario esté aquí

@pytest.fixture
def test_client():
    """Fixture para el cliente de pruebas."""
    app = create_app('testing')  # Configuración de prueba
    with app.test_client() as client:
        with app.app_context():
            # Limpiar y crear la base de datos
            db.drop_all()
            db.create_all()
            
            # Crear un usuario de prueba
            user = User(email="user1@example.com", password="1234")  # Asegúrate de que el campo password esté configurado correctamente
            db.session.add(user)
            db.session.commit()

            # Crear un DSMetaData de prueba
            ds_meta_data = DSMetaData(
                title="Test Metadata", 
                description="Test Description",
                publication_type=PublicationType.BOOK
            )
            db.session.add(ds_meta_data)
            db.session.commit()

            # Crear un dataset de prueba asociado al DSMetaData
            dataset = DataSet(
                name="Test Dataset", 
                user_id=user.id, 
                ds_meta_data_id=ds_meta_data.id
            )
            db.session.add(dataset)
            db.session.commit()

            # Iniciar sesión como el usuario de prueba dentro de una solicitud HTTP activa
            login_user(user)
            
            # Ahora que el usuario está autenticado, yield el cliente para las pruebas
            yield client


def test_rate_dataset_get(test_client):
    """Prueba GET de la ruta de calificación."""
    # Realizar la solicitud GET
    response = test_client.get('/dataset/1/rate')
    
    # Asegúrate de que la respuesta sea la esperada
    assert response.status_code == 200
    assert b'Rate this dataset' in response.data  # Asegúrate de que la página se renderiza correctamente


def test_rate_dataset_post(test_client):
    """Prueba POST de la ruta de calificación."""
    # Realizar la solicitud POST con los datos de calificación
    response = test_client.post('/dataset/1/rate', data={'score': 5})
    
    # Asegúrate de que la respuesta sea la esperada (redirección o éxito)
    assert response.status_code == 302  # Redirección después de una calificación exitosa
    assert b'Dataset has been rated' in response.data  # Confirma que la calificación se ha guardado


def test_rate_dataset_post_with_invalid_data(test_client):
    """Prueba POST con datos inválidos para la calificación."""
    # Realizar la solicitud POST con datos inválidos
    response = test_client.post('/dataset/1/rate', data={'score': 0})  # Suponiendo que el 0 no sea un valor válido
    
    # Asegúrate de que la respuesta sea la esperada (error o mensaje adecuado)
    assert response.status_code == 400  # Código de error
    assert b'Invalid score' in response.data  # Asegúrate de que el error se muestra correctamente


def test_rate_dataset_redirect_on_success(test_client):
    """Prueba que se redirige correctamente después de calificar."""
    # Realizar la solicitud POST para calificar
    response = test_client.post('/dataset/1/rate', data={'score': 5})
    
    # Verificar la redirección después de calificar
    assert response.status_code == 302  # Redirección después de calificar
    assert response.location == 'http://localhost/dataset/1'  # Verificar la URL de redirección
