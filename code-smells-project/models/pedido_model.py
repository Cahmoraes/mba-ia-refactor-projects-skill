from infrastructure.database import Database


def _serialize_pedido(row) -> dict:
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
        "itens": [],
    }


def _attach_itens(db: Database, pedidos: list[dict]) -> list[dict]:
    """Single round-trip to collect all itens + product names for a batch of pedidos."""
    if not pedidos:
        return pedidos
    ids = [p["id"] for p in pedidos]
    placeholders = ",".join("?" * len(ids))
    rows = db.execute(
        f"""
        SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
        FROM itens_pedido ip
        LEFT JOIN produtos p ON p.id = ip.produto_id
        WHERE ip.pedido_id IN ({placeholders})
        """,
        ids,
    ).fetchall()
    grouped: dict[int, list[dict]] = {}
    for r in rows:
        grouped.setdefault(r["pedido_id"], []).append({
            "produto_id": r["produto_id"],
            "produto_nome": r["produto_nome"] or "Desconhecido",
            "quantidade": r["quantidade"],
            "preco_unitario": r["preco_unitario"],
        })
    for pedido in pedidos:
        pedido["itens"] = grouped.get(pedido["id"], [])
    return pedidos


def list_all(db: Database) -> list[dict]:
    rows = db.execute("SELECT * FROM pedidos").fetchall()
    pedidos = [_serialize_pedido(r) for r in rows]
    return _attach_itens(db, pedidos)


def list_by_user(db: Database, usuario_id: int) -> list[dict]:
    rows = db.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
    pedidos = [_serialize_pedido(r) for r in rows]
    return _attach_itens(db, pedidos)


def update_status(db: Database, pedido_id: int, novo_status: str) -> None:
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()


def fetch_produto(db: Database, produto_id: int):
    return db.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (produto_id,)).fetchone()


def insert_pedido(db: Database, usuario_id: int, total: float) -> int:
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    return cursor.lastrowid


def insert_item(db: Database, pedido_id: int, produto_id: int, quantidade: int, preco_unitario: float) -> None:
    db.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def decrement_estoque(db: Database, produto_id: int, quantidade: int) -> None:
    db.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id),
    )


def count(db: Database) -> int:
    return db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]


def report_metrics(db: Database) -> dict:
    row = db.execute(
        """
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(total), 0) AS faturamento,
            SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pendentes,
            SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) AS aprovados,
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM pedidos
        """
    ).fetchone()
    return {
        "total": row["total"] or 0,
        "faturamento": row["faturamento"] or 0,
        "pendentes": row["pendentes"] or 0,
        "aprovados": row["aprovados"] or 0,
        "cancelados": row["cancelados"] or 0,
    }
