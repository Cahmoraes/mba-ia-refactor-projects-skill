"""Composition root — wires Flask, config, infrastructure, routes and middlewares."""
import logging

from flask import Flask
from flask_cors import CORS

from config.settings import settings
from infrastructure.database import get_database
from middlewares.error_handler import register_error_handlers
from routes.health_routes import health_bp
from routes.pedido_routes import pedido_bp
from routes.produto_routes import produto_bp
from routes.relatorio_routes import relatorio_bp
from routes.usuario_routes import usuario_bp

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    # Initialize DB schema + seed at startup.
    get_database()

    app.register_blueprint(health_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)

    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
