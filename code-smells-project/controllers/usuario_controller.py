import logging

from werkzeug.security import check_password_hash, generate_password_hash

from infrastructure.database import Database
from middlewares.error_handler import AppError
from middlewares.validators import validate_login_payload, validate_usuario_payload
from models import usuario_model

logger = logging.getLogger("app.usuarios")


def listar(db: Database) -> list[dict]:
    return usuario_model.list_all(db)


def buscar(db: Database, user_id: int) -> dict:
    user = usuario_model.find_by_id(db, user_id)
    if not user:
        raise AppError("Usuário não encontrado", 404)
    return user


def criar(db: Database, payload: dict) -> int:
    data = validate_usuario_payload(payload)
    senha_hash = generate_password_hash(data["senha"])
    try:
        return usuario_model.create(db, nome=data["nome"], email=data["email"], senha_hash=senha_hash)
    except Exception as err:
        msg = str(err).lower()
        if "unique" in msg or "constraint" in msg:
            raise AppError("Email já cadastrado", 409)
        raise


def login(db: Database, payload: dict) -> dict:
    creds = validate_login_payload(payload)
    user = usuario_model.find_by_email_with_secret(db, creds["email"])
    if not user:
        raise AppError("Credenciais inválidas", 401)
    if not check_password_hash(user["senha_hash"], creds["senha"]):
        # Allow login for legacy plaintext rows by re-hashing on the fly when they match.
        if user["senha_hash"] != creds["senha"]:
            raise AppError("Credenciais inválidas", 401)
        # Upgrade the stored credential to a proper hash on a successful legacy login.
        new_hash = generate_password_hash(creds["senha"])
        db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (new_hash, user["id"]))
        db.commit()
        logger.info("upgraded legacy password user_id=%s", user["id"])

    return {
        "id": user["id"],
        "nome": user["nome"],
        "email": user["email"],
        "tipo": user["tipo"],
    }
