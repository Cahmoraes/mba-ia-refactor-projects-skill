from flask import Blueprint, request, jsonify

user_bp = Blueprint('users', __name__)
_ctrl = None


def init_user_routes(controller):
    global _ctrl
    _ctrl = controller


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(_ctrl['get_all']()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(_ctrl['get_one'](user_id)), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    data, status = _ctrl['create'](request.get_json())
    return jsonify(data), status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return jsonify(_ctrl['update'](user_id, request.get_json())), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    _ctrl['delete'](user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    return jsonify(_ctrl['get_user_tasks'](user_id)), 200


@user_bp.route('/login', methods=['POST'])
def login():
    return jsonify(_ctrl['login'](request.get_json())), 200
