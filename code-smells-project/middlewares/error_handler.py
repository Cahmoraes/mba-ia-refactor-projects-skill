import logging

from flask import Flask, jsonify

logger = logging.getLogger("app.errors")


class AppError(Exception):
    """Domain error raised by controllers — caught by the centralized handler."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def _app_error(err: AppError):
        return jsonify({"erro": err.message, "sucesso": False}), err.status

    @app.errorhandler(404)
    def _not_found(_):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(405)
    def _method_not_allowed(_):
        return jsonify({"erro": "Método não permitido", "sucesso": False}), 405

    @app.errorhandler(Exception)
    def _generic(err: Exception):
        logger.exception("unhandled exception")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
