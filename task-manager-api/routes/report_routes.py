from flask import Blueprint, request, jsonify

report_bp = Blueprint('reports', __name__)
_ctrl = None


def init_report_routes(controller):
    global _ctrl
    _ctrl = controller


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(_ctrl['summary']()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return jsonify(_ctrl['user_report'](user_id)), 200


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(_ctrl['get_categories']()), 200


@report_bp.route('/categories', methods=['POST'])
def create_category():
    data, status = _ctrl['create_category'](request.get_json())
    return jsonify(data), status


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    return jsonify(_ctrl['update_category'](cat_id, request.get_json())), 200


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    _ctrl['delete_category'](cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
