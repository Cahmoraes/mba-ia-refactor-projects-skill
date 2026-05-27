from typing import Optional

from infrastructure.database import Database


def _serialize(row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def list_all(db: Database) -> list[dict]:
    rows = db.execute("SELECT * FROM produtos").fetchall()
    return [_serialize(r) for r in rows]


def find_by_id(db: Database, produto_id: int) -> Optional[dict]:
    row = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return _serialize(row) if row else None


def create(db: Database, nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> int:
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def update(db: Database, produto_id: int, nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> None:
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def delete(db: Database, produto_id: int) -> None:
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def search(db: Database, termo: Optional[str], categoria: Optional[str], preco_min: Optional[float], preco_max: Optional[float]) -> list[dict]:
    clauses: list[str] = []
    values: list = []
    if termo:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        values.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        clauses.append("categoria = ?")
        values.append(categoria)
    if preco_min is not None:
        clauses.append("preco >= ?")
        values.append(preco_min)
    if preco_max is not None:
        clauses.append("preco <= ?")
        values.append(preco_max)

    query = "SELECT * FROM produtos"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    rows = db.execute(query, values).fetchall()
    return [_serialize(r) for r in rows]


def count(db: Database) -> int:
    return db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
