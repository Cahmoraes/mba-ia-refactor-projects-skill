from flask import Blueprint, jsonify

from controllers import relatorio_controller
from infrastructure.database import get_database

relatorio_bp = Blueprint("relatorios", __name__)


@relatorio_bp.get("/relatorios/vendas")
def relatorio_vendas():
    return jsonify({"dados": relatorio_controller.vendas(get_database()), "sucesso": True}), 200
