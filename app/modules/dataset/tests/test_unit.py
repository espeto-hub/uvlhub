import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from datetime import datetime
from app.modules.dataset.routes import dataset_bp


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


if __name__ == "__main__":
    pytest.main()
