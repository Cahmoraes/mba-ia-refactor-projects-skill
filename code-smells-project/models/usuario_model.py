from typing import Optional

from infrastructure.database import Database


def _public(row) -> dict:
    """Serialize WITHOUT password — output crosses the HTTP boundary."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def list_all(db: Database) -> list[dict]:
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [_public(r) for r in rows]


def find_by_id(db: Database, user_id: int) -> Optional[dict]:
    row = db.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    return _public(row) if row else None


def find_by_email_with_secret(db: Database, email: str) -> Optional[dict]:
    """Internal-only — returns row including the password hash."""
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "senha_hash": row["senha"],
        "tipo": row["tipo"],
    }


def create(db: Database, nome: str, email: str, senha_hash: str, tipo: str = "cliente") -> int:
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def count(db: Database) -> int:
    return db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
