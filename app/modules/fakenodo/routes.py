import os
import tempfile
from flask import request, jsonify, send_file
from . import fakenodo_bp

# Almacenamiento temporal de datasets
datasets_storage = {}
dataset_id_counter = 1


@fakenodo_bp.route('/fakenodo/upload', methods=['POST'])
def handle_upload():
    """
    Handle file uploads for the FakeNODO service.
    Receives a file and stores it temporarily, returning a dataset ID.
    """
    global dataset_id_counter
    uploaded_file = request.files.get('file')

    if uploaded_file:
        # Asigna un ID único a cada dataset
        dataset_id = dataset_id_counter
        dataset_id_counter += 1

        # Crea un directorio temporal para guardar el archivo
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, uploaded_file.filename)
        
        # Guarda el archivo
        uploaded_file.save(file_path)

        # Almacena la información del dataset
        datasets_storage[dataset_id] = {
            'id': dataset_id,
            'filename': uploaded_file.filename,
            'file_path': file_path
        }

        # Responde con el ID del dataset y el nombre del archivo
        return jsonify({'dataset_id': dataset_id, 'filename': uploaded_file.filename}), 201

    return jsonify({'error': 'No file uploaded'}), 400


@fakenodo_bp.route('/fakenodo/download/<int:dataset_id>', methods=['GET'])
def handle_download(dataset_id):
    """
    Retrieve and send the dataset file for download based on its ID.
    """
    dataset = datasets_storage.get(dataset_id)

    if dataset:
        # Envía el archivo como una respuesta de descarga
        return send_file(dataset['file_path'], as_attachment=True, download_name=dataset['filename'])

    return jsonify({'error': 'Dataset not found'}), 404


@fakenodo_bp.route('/fakenodo/datasets', methods=['GET'])
def list_all_datasets():
    """
    List all available datasets in FakeNODO.
    """
    return jsonify(list(datasets_storage.values()))


@fakenodo_bp.route('/fakenodo/dataset/<int:dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """
    Delete a specific dataset based on its ID.
    """
    dataset = datasets_storage.pop(dataset_id, None)

    if dataset:
        # Elimina el archivo del sistema de archivos
        os.remove(dataset['file_path'])
        return jsonify({'message': 'Dataset deleted successfully'}), 200

    return jsonify({'error': 'Dataset not found'}), 404
