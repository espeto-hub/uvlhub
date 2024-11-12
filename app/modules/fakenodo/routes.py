from flask import jsonify, make_response
from app.modules.fakenodo import fakenodo_bp


@fakenodo_bp.route("/fakenodo/api", methods=["GET"])
def test_fakenodo_connection():
    response = {"status": "success", "message": "You have successfully connected to Fakenodo"}
    return jsonify(response)


@fakenodo_bp.route("/fakenodo/api", methods=["POST"])
def create_deposition():
    response = {"status": "success", "message": "You have successfully created a deposition in Fakenodo"}
    return make_response(jsonify(response), 201)


@fakenodo_bp.route("/fakenodo/api/<deposition_id>/files", methods=["POST"])
def create_deposition_files(depositionId):
    response = {"status": "success", "message": "You have successfuly uploaded deposition files  in Fakenodo."}
    return make_response(jsonify(response), 201)


@fakenodo_bp.route("/fakenodo/api/<deposition_id>", methods=["DELETE"])
def delete_deposition(depositionId):
    response = {"status": "success", "message": "You hace successfully deleted a deposition in Fakenodo"}
    return make_response(jsonify(response), 200)


@fakenodo_bp.route("/fakenodo/api/<deposition_id>/actions/publish", methods=["POST"])
def publish_deposition(depositionId):
    response = {"status": "success", "message": "You have successfully published a deposition in Fakenodo"}
    return make_response(jsonify(response), 202)


@fakenodo_bp.route("/fakenodo/api/<deposition_id>", methods=["GET"])
def get_deposition(depositionId):
    response = {
        "status": "success", "message": "You have successfully retrieved a deposition in Fakenodo",
        "doi": "10.5072/fakenodo.123456",
    }
    return make_response(jsonify(response), 200)
