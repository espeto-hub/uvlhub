import logging
import os

from app.modules.dataset.models import Dataset
from app.modules.fakenodo.repositories import DatasetRepository
from app.modules.featuremodel.models import FeatureModel

from core.configuration.configuration import uploads_folder_name
from dotenv import load_dotenv
from flask_login import current_user
from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)

load_dotenv()


class FakenodoService(BaseService):

    def __init__(self):
        # Cambié DepositionRepository por DatasetRepository
        self.dataset_repository = DatasetRepository()

    def create_new_dataset(self, dataset) -> dict:
        """
        Crear un nuevo dataset en Fakenodo.
        Args:
            dataset (Dataset): El objeto Dataset que contiene los metadatos del dataset.
        Returns:
            dict: La respuesta en formato JSON con los detalles del dataset creado.
        """
        logger.info("Dataset enviando a Fakenodo...")
        logger.info(f"Tipo de publicación...{dataset.ds_meta_data.publication_type.value}")

        metadata = {
            "title": dataset.ds_meta_data.title,
            "upload_type": "dataset" if dataset.ds_meta_data.publication_type.value == "none" else "publication",
            "publication_type": (
                dataset.ds_meta_data.publication_type.value
                if dataset.ds_meta_data.publication_type.value != "none"
                else None
            ),
            "description": dataset.ds_meta_data.description,
            "creators": [
                {
                    "name": author.name,
                    **({"affiliation": author.affiliation} if author.affiliation else {}),
                    **({"orcid": author.orcid} if author.orcid else {}),
                }
                for author in dataset.ds_meta_data.authors
            ],
            "keywords": (
                ["uvlhub"] if not dataset.ds_meta_data.tags else dataset.ds_meta_data.tags.split(", ") + ["uvlhub"]
            ),
            "access_right": "open",
            "license": "CC-BY-4.0",
        }

        try:
            # Crear el nuevo dataset usando el DatasetRepository
            new_dataset = self.dataset_repository.create_new_dataset(dataset_metadata=metadata)

            return {
                "id": new_dataset.id,
                "metadata": metadata,
                "message": "Dataset creado correctamente en Fakenodo."
            }
        except Exception as e:
            raise Exception(f"Error al crear el dataset: {str(e)}")

    def upload_file(self, dataset: Dataset, dataset_id: int, feature_model: FeatureModel, user=None) -> dict:
        """
        Subir un archivo a un dataset en Fakenodo.
        Args:
            dataset_id (int): El ID del dataset.
            feature_model (FeatureModel): El objeto FeatureModel que representa el modelo de características.
            user (FeatureModel): El objeto de Usuario que representa al propietario del archivo.
        Returns:
            dict: La respuesta en formato JSON con los detalles del archivo subido.
        """
        uvl_filename = feature_model.fm_meta_data.uvl_filename
        user_id = current_user.id if user is None else user.id
        file_path = os.path.join(uploads_folder_name(), f"user_{str(user_id)}", f"dataset_{dataset.id}/", uvl_filename)

        response = {
            "id": dataset_id,
            "filename": uvl_filename,
            "filesize": os.path.getsize(file_path),
            "checksum": calculate_checksum(file_path),
            "message": "Archivo subido correctamente a Fakenodo."
        }

        return response

    def publish_dataset(self, dataset_id: int) -> dict:
        """
        Publicar un dataset en Fakenodo.
        Args:
            dataset_id (int): El ID del dataset en Fakenodo.
        Returns:
            dict: La respuesta en formato JSON con los detalles del dataset publicado.
        """
        dataset = Dataset.query.get(dataset_id)
        if not dataset:
            raise Exception("Dataset no encontrado")

        try:
            dataset.doi = f"10.5281/fakenodo.{dataset_id}"
            dataset.status = "published"
            self.dataset_repository.update(dataset)

            response = {
                "id": dataset_id,
                "status": "published",
                "conceptdoi": f"10.5281/fakenodo.{dataset_id}",
                "message": "Dataset publicado correctamente en Fakenodo."
            }
            return response

        except Exception as e:
            raise Exception(f"Error al publicar el dataset: {str(e)}")

    def get_dataset(self, dataset_id: int) -> dict:
        """
        Obtener un dataset desde Fakenodo.
        Args:
            dataset_id (int): El ID del dataset en Fakenodo.
        Returns:
            dict: La respuesta en formato JSON con los detalles del dataset.
        """
        dataset = Dataset.query.get(dataset_id)
        if not dataset:
            raise Exception("Dataset no encontrado")

        response = {
            "id": dataset.id,
            "doi": dataset.doi,
            "metadata": dataset.metadata,  # Suponiendo que tienes un campo `metadata` en el modelo Dataset
            "status": dataset.status,
            "message": "Dataset recuperado correctamente de Fakenodo."
        }
        return response

    def get_doi(self, dataset_id: int) -> str:
        """
        Obtener el DOI de un dataset desde Fakenodo.
        Args:
            dataset_id (int): El ID del dataset en Fakenodo.
        Returns:
            str: El DOI del dataset.
        """
        return self.get_dataset(dataset_id).get("doi")


def calculate_checksum(file_path):
    import hashlib
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
