
from unittest.mock import patch
import pytest
from app.modules.dataset.repositories import DSMetaDataRepository
from app.modules.dataset.models import Rating
from app.modules.dataset.services import Rating as DatasetRatingService



@pytest.fixture(scope="module")
def test_count_dsmetadata_calls_repository():
    """Test that count_dsmetadata calls the repository's count method."""
    with patch("app.modules.dataset.repositories.DSMetaDataRepository.count") as mock_count:
        mock_count.return_value = 20

        # Crear un objeto DSMetaDataRepository
        repo = DSMetaDataRepository()
        result = repo.count()

        # Verificar que el método count fue llamado y devuelve el valor correcto
        mock_count.assert_called_once()
        assert result == 20


@pytest.fixture(scope="module")
def test_rate_for_first_time_creates_new_rating():
    """Test creating a new rating for a dataset."""
    with patch("app.modules.dataset.repositories.RatingRepository.add_rating") as mock_add_rating, \
            patch("app.modules.dataset.repositories.RatingRepository.find_user_rating") as mock_find_rating:

        # Crear mocks para las dependencias
        mock_find_rating.return_value = None
        mock_add_rating.return_value = Rating(rate=5, dataset_id=1, user_id=1)

        # Crear instancia del servicio
        service = DatasetRatingService()

        # Probar el método submit_rating
        dataset_id = 1
        user_id = 1
        rate = 5
        result = service.submit_rating(dataset_id, user_id, rate)

        # Validar comportamiento
        mock_find_rating.assert_called_once_with(dataset_id, user_id)
        mock_add_rating.assert_called_once_with(dataset_id, user_id, rate)
        assert result.rate == rate
        assert result.dataset_id == dataset_id
        assert result.user_id == user_id


@pytest.fixture(scope="module")
def test_update_existing_rating():
    """Test updating an existing rating."""
    with patch("app.modules.dataset.repositories.RatingRepository.find_user_rating") as mock_find_rating, \
            patch("app.modules.dataset.repositories.RatingRepository.update_rating") as mock_update_rating:

        # Simular la existencia de un rating previo
        existing_rating = Rating(rate=3, dataset_id=1, user_id=1)
        mock_find_rating.return_value = existing_rating

        # Crear instancia del servicio
        service = DatasetRatingService()

        # Actualizar el rating
        dataset_id = 1
        user_id = 1
        new_rate = 5
        result = service.submit_rating(dataset_id, user_id, new_rate)

        # Validar que se actualizó correctamente
        mock_find_rating.assert_called_once_with(dataset_id, user_id)
        mock_update_rating.assert_called_once_with(existing_rating, new_rate)
        assert result.rate == new_rate


@pytest.fixture(scope="module")
def test_calculate_average_rating():
    """Test calculating the average rating for a dataset."""
    with patch("app.modules.dataset.repositories.RatingRepository.get_all_ratings") as mock_get_all_ratings:
        mock_get_all_ratings.return_value = [
            Rating(rate=5, dataset_id=1, user_id=1),
            Rating(rate=4, dataset_id=1, user_id=2),
            Rating(rate=3, dataset_id=1, user_id=3),
        ]

        # Crear instancia del servicio
        service = DatasetRatingService()

        # Calcular el promedio
        dataset_id = 1
        result = service.get_average_rating(dataset_id)

        # Validar que el promedio es correcto
        mock_get_all_ratings.assert_called_once_with(dataset_id)
        assert result == 4  # (5 + 4 + 3) / 3


@pytest.fixture(scope="module")
def test_find_rating_by_user_and_dataset():
    """Test finding a rating by user and dataset."""
    with patch("app.modules.dataset.repositories.RatingRepository.find_user_rating") as mock_find_rating:
        mock_rating = Rating(rate=5, dataset_id=1, user_id=1)
        mock_find_rating.return_value = mock_rating

        # Crear instancia del servicio
        service = DatasetRatingService()

        # Probar la búsqueda
        dataset_id = 1
        user_id = 1
        result = service.find_rating_by_user_and_dataset(dataset_id, user_id)

        # Validar que el resultado es correcto
        mock_find_rating.assert_called_once_with(dataset_id, user_id)
        assert result == mock_rating


@pytest.fixture(scope="module")
def test_multiple_users_rate_same_dataset():
    """Test that multiple users can rate the same dataset."""
    with patch("app.modules.dataset.repositories.RatingRepository.add_rating") as mock_add_rating:

        # Crear instancia del servicio
        service = DatasetRatingService()

        # Probar múltiples ratings
        dataset_id = 1
        ratings = [(1, 4), (2, 5), (3, 3)]  # (user_id, rate)

        for user_id, rate in ratings:
            service.submit_rating(dataset_id, user_id, rate)
            mock_add_rating.assert_called_with(dataset_id, user_id, rate)
            mock_add_rating.reset_mock()
