from flask import Blueprint, request, jsonify

task_bp = Blueprint('tasks', __name__)
_ctrl = None


def init_task_routes(controller):
    global _ctrl
    _ctrl = controller


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(_ctrl['get_all']()), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    result = _ctrl['search'](
        q=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify(result), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(_ctrl['stats']()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return jsonify(_ctrl['get_one'](task_id)), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data, status = _ctrl['create'](request.get_json())
    return jsonify(data), status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    return jsonify(_ctrl['update'](task_id, request.get_json())), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    _ctrl['delete'](task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200
