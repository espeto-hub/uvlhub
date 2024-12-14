import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from datetime import datetime
from app.modules.dataset.routes import dataset_bp
from app.modules.dataset.services import RatingService
from app.modules.dataset.models import Rating, DataSet
from sqlalchemy.exc import IntegrityError


# --- Tests existentes para descarga de datasets ---

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(dataset_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('app.modules.dataset.routes.dataset_service.zip_all_datasets')
@patch('app.modules.dataset.routes.send_file')
def test_download_all_dataset(mock_send_file, mock_zip_all_datasets, client):
    # Configurar el mock para que devuelva un valor específico
    mock_zip_all_datasets.return_value = '/path/to/all_datasets.zip'
    mock_send_file.return_value = MagicMock()

    # Realizar una solicitud GET a la ruta de descarga de todos los datasets
    response = client.get('/dataset/download/all')

    # Verificar que la respuesta tiene el código de estado 200
    assert response.status_code == 200

    # Verificar que zip_all_datasets fue llamado una vez
    mock_zip_all_datasets.assert_called_once()

    # Verificar que send_file fue llamado con los argumentos correctos
    current_date = datetime.now().strftime("%Y_%m_%d")
    zip_filename = f"uvlhub_bulk_{current_date}.zip"
    mock_send_file.assert_called_once_with('/path/to/all_datasets.zip', as_attachment=True, download_name=zip_filename)


# --- Nuevos tests para el servicio de Rating ---

@pytest.fixture
def mock_db_session():
    """Fixture para proporcionar una sesión de base de datos simulada."""
    return MagicMock()


@pytest.fixture
def rating_service(mock_db_session):
    """Fixture para inicializar el servicio de rating."""
    return RatingService(db_session=mock_db_session)


@patch('flask.flash')  # Mock para flash
def test_save_rating_creates_new(mock_flash, rating_service, mock_db_session):
    """Probar que se crea una nueva calificación si no existe."""

    no_rating = MagicMock(spec=Rating, score=None)
    mock_db_session.query().filter_by().first.return_value = no_rating

    # Ejecutar el método
    rating_service.save_rating(dataset_id=1, user_id=1, score=5)

    # Verificar que la calificación fue actualizada
    assert no_rating.score == 5
    mock_db_session.commit.assert_called_once()


def test_save_rating_updates_existing(client, rating_service, mock_db_session):
    """Probar que se actualiza una calificación existente."""
    # Configurar mock para que haya una calificación previa
    existing_rating = MagicMock(spec=Rating, score=3)
    mock_db_session.query().filter_by().first.return_value = existing_rating

    # Ejecutar el método
    rating_service.save_rating(dataset_id=1, user_id=1, score=5)

    # Verificar que la calificación fue actualizada
    assert existing_rating.score == 5
    mock_db_session.commit.assert_called_once()


def test_get_average_rating(rating_service, mock_db_session):
    """Probar que el promedio de calificaciones se calcula correctamente."""
    # Configurar mock para devolver un conjunto de calificaciones
    mock_db_session.query().filter_by().all.return_value = [(5,), (4,), (3,)]

    # Ejecutar el método
    average = rating_service.get_average_rating(dataset_id=1)

    # Verificar el promedio calculado
    assert average == 4.0
