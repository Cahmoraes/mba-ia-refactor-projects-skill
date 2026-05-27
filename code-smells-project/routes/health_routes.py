from flask import Blueprint, jsonify

from controllers import health_controller
from infrastructure.database import get_database

health_bp = Blueprint("health", __name__)


@health_bp.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "2.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@health_bp.get("/health")
def health():
    return jsonify({**health_controller.health_check(get_database()), "sucesso": True}), 200
