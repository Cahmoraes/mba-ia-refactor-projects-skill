from flask import Blueprint, jsonify, request

from controllers import produto_controller
from infrastructure.database import get_database

produto_bp = Blueprint("produtos", __name__)


@produto_bp.get("/produtos")
def listar_produtos():
    return jsonify({"dados": produto_controller.listar(get_database()), "sucesso": True}), 200


@produto_bp.get("/produtos/busca")
def buscar_produtos():
    args = request.args
    resultados = produto_controller.buscar_filtrado(
        get_database(),
        termo=args.get("q", ""),
        categoria=args.get("categoria"),
        preco_min=args.get("preco_min"),
        preco_max=args.get("preco_max"),
    )
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@produto_bp.get("/produtos/<int:id>")
def buscar_produto(id: int):
    return jsonify({"dados": produto_controller.buscar(get_database(), id), "sucesso": True}), 200


@produto_bp.post("/produtos")
def criar_produto():
    novo_id = produto_controller.criar(get_database(), request.get_json(silent=True))
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


@produto_bp.put("/produtos/<int:id>")
def atualizar_produto(id: int):
    produto_controller.atualizar(get_database(), id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@produto_bp.delete("/produtos/<int:id>")
def deletar_produto(id: int):
    produto_controller.deletar(get_database(), id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
