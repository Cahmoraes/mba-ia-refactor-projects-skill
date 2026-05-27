import datetime
from flask import Flask
from flask_cors import CORS

from config.settings import settings
from database import db
from middlewares.error_handler import register_error_handlers

from controllers.task_controller import build_task_controller
from controllers.user_controller import build_user_controller
from controllers.report_controller import build_report_controller
from services.notification_service import NotificationService

from routes.task_routes import task_bp, init_task_routes
from routes.user_routes import user_bp, init_user_routes
from routes.report_routes import report_bp, init_report_routes


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{settings.DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    CORS(app)
    db.init_app(app)

    notification_service = NotificationService()
    task_ctrl = build_task_controller(notification_service)
    user_ctrl = build_user_controller()
    report_ctrl = build_report_controller()

    init_task_routes(task_ctrl)
    init_user_routes(user_ctrl)
    init_report_routes(report_ctrl)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    register_error_handlers(app)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.datetime.utcnow())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '2.0'}

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
