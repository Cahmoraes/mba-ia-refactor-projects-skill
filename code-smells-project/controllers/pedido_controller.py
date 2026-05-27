import logging

from infrastructure.database import Database
from middlewares.error_handler import AppError
from middlewares.validators import validate_pedido_payload, validate_status_pedido
from models import pedido_model

logger = logging.getLogger("app.pedidos")


def criar(db: Database, payload: dict) -> dict:
    data = validate_pedido_payload(payload)
    usuario_id, itens = data["usuario_id"], data["itens"]

    # Pre-fetch and validate produtos for every item before mutating anything.
    enriched_itens = []
    total = 0.0
    for item in itens:
        produto = pedido_model.fetch_produto(db, item["produto_id"])
        if produto is None:
            raise AppError(f"Produto {item['produto_id']} não encontrado", 404)
        if produto["estoque"] < item["quantidade"]:
            raise AppError(f"Estoque insuficiente para {produto['nome']}", 400)
        enriched_itens.append({
            "produto_id": produto["id"],
            "quantidade": item["quantidade"],
            "preco_unitario": produto["preco"],
        })
        total += produto["preco"] * item["quantidade"]

    pedido_id = pedido_model.insert_pedido(db, usuario_id=usuario_id, total=total)
    for it in enriched_itens:
        pedido_model.insert_item(
            db,
            pedido_id=pedido_id,
            produto_id=it["produto_id"],
            quantidade=it["quantidade"],
            preco_unitario=it["preco_unitario"],
        )
        pedido_model.decrement_estoque(db, produto_id=it["produto_id"], quantidade=it["quantidade"])

    db.commit()
    logger.info("pedido created pedido_id=%s usuario_id=%s total=%s", pedido_id, usuario_id, total)
    return {"pedido_id": pedido_id, "total": round(total, 2)}


def listar_todos(db: Database) -> list[dict]:
    return pedido_model.list_all(db)


def listar_por_usuario(db: Database, usuario_id: int) -> list[dict]:
    return pedido_model.list_by_user(db, usuario_id)


def atualizar_status(db: Database, pedido_id: int, payload: dict) -> str:
    status = validate_status_pedido(payload)
    pedido_model.update_status(db, pedido_id, status)
    logger.info("pedido status updated pedido_id=%s status=%s", pedido_id, status)
    return status
