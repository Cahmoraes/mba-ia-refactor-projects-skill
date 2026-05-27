from flask import Blueprint, jsonify, request

from controllers import usuario_controller
from infrastructure.database import get_database

usuario_bp = Blueprint("usuarios", __name__)


@usuario_bp.get("/usuarios")
def listar_usuarios():
    return jsonify({"dados": usuario_controller.listar(get_database()), "sucesso": True}), 200


@usuario_bp.get("/usuarios/<int:id>")
def buscar_usuario(id: int):
    return jsonify({"dados": usuario_controller.buscar(get_database(), id), "sucesso": True}), 200


@usuario_bp.post("/usuarios")
def criar_usuario():
    novo_id = usuario_controller.criar(get_database(), request.get_json(silent=True))
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


@usuario_bp.post("/login")
def login():
    user = usuario_controller.login(get_database(), request.get_json(silent=True))
    return jsonify({"dados": user, "sucesso": True, "mensagem": "Login OK"}), 200
