from unittest.mock import MagicMock, patch
from app import create_app
from app.modules.dataset.models import Rating


def test_count_dsmetadata(dataset_service):
    """Test counting metadata entries."""
    with patch.object(dataset_service, 'dsmetadata_repository', MagicMock()) as dsmetadata_repository_mock:
        dsmetadata_repository_mock.count.return_value = 20
        result = dataset_service.count_dsmetadata()
        assert result == 20


def test_rate_for_first_time(dataset_rating_service):
    """Test submitting a rating for the first time."""
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'add_rating') as mock_submit_rating, \
                patch.object(dataset_rating_service.repository, 'find_user_rating') as mock_find_rating:

            # Mock behaviors
            mock_submit_rating.return_value = MagicMock(rate=5, dataset_id=1, user_id=1)
            mock_find_rating.return_value = None

            dataset_id = 1
            user_id = 1
            rate = 5
            result = dataset_rating_service.submit_rating(dataset_id, user_id, rate)

            assert result.rate == rate
            assert result.dataset_id == dataset_id
            assert result.user_id == user_id
            mock_submit_rating.assert_called_once_with(dataset_id, user_id, rate)


def test_update_rate(dataset_rating_service):
    """Test updating an existing rating."""
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'find_user_rating') as mock_find_rating, \
                patch.object(dataset_rating_service.repository, 'update_rating') as mock_update_rating:

            # Mock old rating
            mock_old_rating = MagicMock(spec=Rating, rate=3, dataset_id=1, user_id=1)
            mock_find_rating.return_value = mock_old_rating

            dataset_id = 1
            user_id = 1
            new_rate = 5

            result = dataset_rating_service.submit_rating(dataset_id, user_id, new_rate)

            assert result == mock_old_rating
            assert mock_old_rating.rate == new_rate
            mock_find_rating.assert_called_once_with(dataset_id, user_id)
            mock_update_rating.assert_called_once_with(mock_old_rating, new_rate)


def test_get_average_rating(dataset_rating_service):
    """Test calculating average rating."""
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'get_all_ratings') as mock_get_all_ratings:
            mock_get_all_ratings.return_value = [
                MagicMock(rate=5),
                MagicMock(rate=4),
                MagicMock(rate=3)
            ]

            dataset_id = 1
            result = dataset_rating_service.get_average_rating(dataset_id)

            assert result == 4  # Average of 5, 4, 3
            mock_get_all_ratings.assert_called_once_with(dataset_id)


def test_find_rating_by_user_and_dataset(dataset_rating_service):
    """Test finding a rating by user and dataset."""
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'find_user_rating') as mock_find_rating:
            mock_rating = MagicMock(rate=5, dataset_id=1, user_id=1)
            mock_find_rating.return_value = mock_rating

            dataset_id = 1
            user_id = 1
            result = dataset_rating_service.find_rating_by_user_and_dataset(dataset_id, user_id)

            assert result == mock_rating
            mock_find_rating.assert_called_once_with(dataset_id, user_id)


def test_multiple_users_rate_same_dataset(dataset_rating_service):
    """Test multiple users rating the same dataset."""
    app = create_app()
    with app.app_context():
        with patch.object(dataset_rating_service.repository, 'add_rating') as mock_submit_rating:

            dataset_id = 1
            ratings = [(1, 4), (2, 5), (3, 3)]  # (user_id, rate)

            for user_id, rate in ratings:
                dataset_rating_service.submit_rating(dataset_id, user_id, rate)
                mock_submit_rating.assert_called_with(dataset_id, user_id, rate)
                mock_submit_rating.reset_mock()