from flask import Blueprint, jsonify, request

from controllers import pedido_controller
from infrastructure.database import get_database

pedido_bp = Blueprint("pedidos", __name__)


@pedido_bp.post("/pedidos")
def criar_pedido():
    resultado = pedido_controller.criar(get_database(), request.get_json(silent=True))
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado"}), 201


@pedido_bp.get("/pedidos")
def listar_todos():
    return jsonify({"dados": pedido_controller.listar_todos(get_database()), "sucesso": True}), 200


@pedido_bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_por_usuario(usuario_id: int):
    return jsonify({"dados": pedido_controller.listar_por_usuario(get_database(), usuario_id), "sucesso": True}), 200


@pedido_bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status(pedido_id: int):
    novo = pedido_controller.atualizar_status(get_database(), pedido_id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado", "status": novo}), 200
