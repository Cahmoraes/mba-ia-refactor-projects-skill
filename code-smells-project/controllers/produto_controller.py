from typing import Optional

from infrastructure.database import Database
from middlewares.error_handler import AppError
from middlewares.validators import validate_produto_payload
from models import produto_model


def listar(db: Database) -> list[dict]:
    return produto_model.list_all(db)


def buscar(db: Database, produto_id: int) -> dict:
    produto = produto_model.find_by_id(db, produto_id)
    if not produto:
        raise AppError("Produto não encontrado", 404)
    return produto


def criar(db: Database, payload: dict) -> int:
    data = validate_produto_payload(dict(payload) if payload else {})
    return produto_model.create(
        db,
        nome=data["nome"],
        descricao=data["descricao"],
        preco=data["preco"],
        estoque=data["estoque"],
        categoria=data["categoria"],
    )


def atualizar(db: Database, produto_id: int, payload: dict) -> None:
    if not produto_model.find_by_id(db, produto_id):
        raise AppError("Produto não encontrado", 404)
    data = validate_produto_payload(dict(payload) if payload else {})
    produto_model.update(
        db,
        produto_id=produto_id,
        nome=data["nome"],
        descricao=data["descricao"],
        preco=data["preco"],
        estoque=data["estoque"],
        categoria=data["categoria"],
    )


def deletar(db: Database, produto_id: int) -> None:
    if not produto_model.find_by_id(db, produto_id):
        raise AppError("Produto não encontrado", 404)
    produto_model.delete(db, produto_id)


def buscar_filtrado(db: Database, termo: Optional[str], categoria: Optional[str], preco_min: Optional[str], preco_max: Optional[str]) -> list[dict]:
    def _to_float(v):
        if v is None or v == "":
            return None
        try:
            return float(v)
        except ValueError:
            raise AppError("Faixa de preço inválida", 400)

    return produto_model.search(db, termo or None, categoria or None, _to_float(preco_min), _to_float(preco_max))
