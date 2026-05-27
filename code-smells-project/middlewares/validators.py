import re
from typing import Optional

from middlewares.error_handler import AppError

CATEGORIAS_VALIDAS = {"informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"}
PEDIDO_STATUSES = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9+_.\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
MIN_PASSWORD_LENGTH = 6


def validate_produto_payload(payload: Optional[dict], partial: bool = False) -> dict:
    if not isinstance(payload, dict):
        raise AppError("Dados inválidos", 400)

    required = {"nome", "preco", "estoque"}
    if not partial:
        missing = required - payload.keys()
        if missing:
            raise AppError(f"Campos obrigatórios ausentes: {', '.join(sorted(missing))}", 400)

    if "nome" in payload:
        nome = (payload.get("nome") or "").strip()
        if len(nome) < 2:
            raise AppError("Nome muito curto", 400)
        if len(nome) > 200:
            raise AppError("Nome muito longo", 400)
        payload["nome"] = nome

    if "preco" in payload:
        try:
            preco = float(payload["preco"])
        except (TypeError, ValueError):
            raise AppError("Preço inválido", 400)
        if preco < 0:
            raise AppError("Preço não pode ser negativo", 400)
        payload["preco"] = preco

    if "estoque" in payload:
        try:
            estoque = int(payload["estoque"])
        except (TypeError, ValueError):
            raise AppError("Estoque inválido", 400)
        if estoque < 0:
            raise AppError("Estoque não pode ser negativo", 400)
        payload["estoque"] = estoque

    categoria = payload.get("categoria", "geral")
    if categoria not in CATEGORIAS_VALIDAS:
        raise AppError(
            f"Categoria inválida. Válidas: {sorted(CATEGORIAS_VALIDAS)}",
            400,
        )
    payload["categoria"] = categoria
    payload.setdefault("descricao", "")
    return payload


def validate_usuario_payload(payload: Optional[dict]) -> dict:
    if not isinstance(payload, dict):
        raise AppError("Dados inválidos", 400)
    nome = (payload.get("nome") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    senha = payload.get("senha") or ""

    if not nome:
        raise AppError("Nome é obrigatório", 400)
    if not email or not EMAIL_REGEX.match(email):
        raise AppError("Email inválido", 400)
    if len(senha) < MIN_PASSWORD_LENGTH:
        raise AppError(f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres", 400)

    return {"nome": nome, "email": email, "senha": senha}


def validate_login_payload(payload: Optional[dict]) -> dict:
    if not isinstance(payload, dict):
        raise AppError("Dados inválidos", 400)
    email = (payload.get("email") or "").strip().lower()
    senha = payload.get("senha") or ""
    if not email or not senha:
        raise AppError("Email e senha são obrigatórios", 400)
    return {"email": email, "senha": senha}


def validate_pedido_payload(payload: Optional[dict]) -> dict:
    if not isinstance(payload, dict):
        raise AppError("Dados inválidos", 400)
    usuario_id = payload.get("usuario_id")
    itens = payload.get("itens", [])
    if not usuario_id:
        raise AppError("usuario_id é obrigatório", 400)
    if not itens or not isinstance(itens, list):
        raise AppError("Pedido deve ter pelo menos 1 item", 400)
    for item in itens:
        if "produto_id" not in item or "quantidade" not in item:
            raise AppError("Cada item precisa de produto_id e quantidade", 400)
        if not isinstance(item["quantidade"], int) or item["quantidade"] <= 0:
            raise AppError("Quantidade inválida", 400)
    return {"usuario_id": int(usuario_id), "itens": itens}


def validate_status_pedido(payload: Optional[dict]) -> str:
    if not isinstance(payload, dict) or "status" not in payload:
        raise AppError("Status é obrigatório", 400)
    status = payload["status"]
    if status not in PEDIDO_STATUSES:
        raise AppError("Status inválido", 400)
    return status
