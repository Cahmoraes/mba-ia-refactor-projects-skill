from flask import jsonify


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({'error': err.message}), err.status

    @app.errorhandler(404)
    def handle_404(_err):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(405)
    def handle_405(_err):
        return jsonify({'error': 'Método não permitido'}), 405

    @app.errorhandler(Exception)
    def handle_generic(err):
        app.logger.exception('Unhandled exception: %s', err)
        return jsonify({'error': 'Erro interno do servidor'}), 500
