from datetime import datetime
from app import db

class Dataset(db.Model):
    __tablename__ = 'fakenodo_datasets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    upload_type = db.Column(db.String(50), nullable=False)  # 'dataset' o 'publication'
    publication_type = db.Column(db.String(50), nullable=True)  # Si es una publicación, el tipo de publicación
    description = db.Column(db.Text, nullable=True)
    creators = db.Column(db.String(255), nullable=True)  # Lista de autores, separados por comas
    keywords = db.Column(db.String(255), nullable=True)  # Palabras clave (tags)
    access_right = db.Column(db.String(50), nullable=False, default="open")
    license = db.Column(db.String(50), nullable=False, default="CC-BY-4.0")
    doi = db.Column(db.String(255), nullable=True)  # DOI generado una vez publicada
    status = db.Column(db.String(50), nullable=False, default="draft")  # draft, published
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con los archivos asociados a este dataset
    files = db.relationship('DatasetFile', backref='dataset', lazy=True)

    def __init__(self, title, upload_type, description=None, creators=None, keywords=None, publication_type=None):
        self.title = title
        self.upload_type = upload_type
        self.description = description
        self.creators = creators
        self.keywords = keywords
        self.publication_type = publication_type

    def to_dict(self):
        """
        Convert the dataset object to a dictionary to be returned as JSON.
        """
        return {
            "id": self.id,
            "title": self.title,
            "upload_type": self.upload_type,
            "publication_type": self.publication_type,
            "description": self.description,
            "creators": self.creators,
            "keywords": self.keywords,
            "access_right": self.access_right,
            "license": self.license,
            "doi": self.doi,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class DatasetFile(db.Model):
    __tablename__ = 'fakenodo_dataset_files'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)  # Ruta donde se guarda el archivo
    file_size = db.Column(db.Integer, nullable=False)  # Tamaño del archivo
    checksum = db.Column(db.String(255), nullable=False)  # Checksum del archivo para verificar la integridad
    dataset_id = db.Column(db.Integer, db.ForeignKey('fakenodo_datasets.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, filename, file_path, file_size, checksum, dataset_id):
        self.filename = filename
        self.file_path = file_path
        self.file_size = file_size
        self.checksum = checksum
        self.dataset_id = dataset_id

    def to_dict(self):
        """
        Convert the dataset file object to a dictionary to be returned as JSON.
        """
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "checksum": self.checksum,
            "dataset_id": self.dataset_id,
            "created_at": self.created_at.isoformat()
        }
