from infrastructure.database import Database
from models import pedido_model

DISCOUNT_TIERS = [
    (10_000, 0.10),
    (5_000, 0.05),
    (1_000, 0.02),
]


def _discount_for(revenue: float) -> float:
    for threshold, rate in DISCOUNT_TIERS:
        if revenue > threshold:
            return revenue * rate
    return 0.0


def vendas(db: Database) -> dict:
    metrics = pedido_model.report_metrics(db)
    faturamento = float(metrics["faturamento"])
    total = int(metrics["total"])
    desconto = _discount_for(faturamento)
    ticket_medio = round(faturamento / total, 2) if total > 0 else 0
    return {
        "total_pedidos": total,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": metrics["pendentes"],
        "pedidos_aprovados": metrics["aprovados"],
        "pedidos_cancelados": metrics["cancelados"],
        "ticket_medio": ticket_medio,
    }
