from infrastructure.database import Database
from models import pedido_model, produto_model, usuario_model


def health_check(db: Database) -> dict:
    return {
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produto_model.count(db),
            "usuarios": usuario_model.count(db),
            "pedidos": pedido_model.count(db),
        },
        "versao": "2.0.0",
    }
