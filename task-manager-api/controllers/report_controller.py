from datetime import datetime, timedelta
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from middlewares.error_handler import AppError


def build_report_controller():

    def summary():
        total_tasks = Task.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()

        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()

        p_counts = {i: Task.query.filter_by(priority=i).count() for i in range(1, 6)}

        all_tasks = Task.query.all()
        overdue_count = 0
        overdue_list = []
        for t in all_tasks:
            if t.is_overdue():
                overdue_count += 1
                overdue_list.append({
                    'id': t.id,
                    'title': t.title,
                    'due_date': str(t.due_date),
                    'days_overdue': (datetime.utcnow() - t.due_date).days,
                })

        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_done = Task.query.filter(
            Task.status == 'done',
            Task.updated_at >= seven_days_ago
        ).count()

        # single pass: group tasks by user_id to avoid N+1
        tasks_by_user = {}
        for t in all_tasks:
            tasks_by_user.setdefault(t.user_id, []).append(t)

        users = User.query.all()
        user_stats = []
        for u in users:
            user_tasks = tasks_by_user.get(u.id, [])
            total = len(user_tasks)
            completed = sum(1 for t in user_tasks if t.status == 'done')
            user_stats.append({
                'user_id': u.id,
                'user_name': u.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
            })

        return {
            'generated_at': str(datetime.utcnow()),
            'overview': {
                'total_tasks': total_tasks,
                'total_users': total_users,
                'total_categories': total_categories,
            },
            'tasks_by_status': {
                'pending': pending,
                'in_progress': in_progress,
                'done': done,
                'cancelled': cancelled,
            },
            'tasks_by_priority': {
                'critical': p_counts[1],
                'high': p_counts[2],
                'medium': p_counts[3],
                'low': p_counts[4],
                'minimal': p_counts[5],
            },
            'overdue': {'count': overdue_count, 'tasks': overdue_list},
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

    def user_report(user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)

        tasks = Task.query.filter_by(user_id=user_id).all()
        total = len(tasks)
        done = pending = in_progress = cancelled = overdue = high_priority = 0

        for t in tasks:
            if t.status == 'done':
                done += 1
            elif t.status == 'pending':
                pending += 1
            elif t.status == 'in_progress':
                in_progress += 1
            elif t.status == 'cancelled':
                cancelled += 1
            if t.priority <= 2:
                high_priority += 1
            if t.is_overdue():
                overdue += 1

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': pending,
                'in_progress': in_progress,
                'cancelled': cancelled,
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
            },
        }

    def get_categories():
        cats = Category.query.all()
        result = []
        for c in cats:
            d = c.to_dict()
            d['task_count'] = Task.query.filter_by(category_id=c.id).count()
            result.append(d)
        return result

    def create_category(data):
        if not data:
            raise AppError('Dados inválidos')
        name = data.get('name')
        if not name:
            raise AppError('Nome é obrigatório')
        cat = Category()
        cat.name = name
        cat.description = data.get('description', '')
        cat.color = data.get('color', '#000000')
        db.session.add(cat)
        db.session.commit()
        return cat.to_dict(), 201

    def update_category(cat_id, data):
        cat = db.session.get(Category, cat_id)
        if not cat:
            raise AppError('Categoria não encontrada', 404)
        if not data:
            raise AppError('Dados inválidos')
        if 'name' in data:
            cat.name = data['name']
        if 'description' in data:
            cat.description = data['description']
        if 'color' in data:
            cat.color = data['color']
        db.session.commit()
        return cat.to_dict()

    def delete_category(cat_id):
        cat = db.session.get(Category, cat_id)
        if not cat:
            raise AppError('Categoria não encontrada', 404)
        db.session.delete(cat)
        db.session.commit()

    return {
        'summary': summary,
        'user_report': user_report,
        'get_categories': get_categories,
        'create_category': create_category,
        'update_category': update_category,
        'delete_category': delete_category,
    }
