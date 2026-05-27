from datetime import datetime
from sqlalchemy.orm import joinedload
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from middlewares.error_handler import AppError


def build_task_controller(notification_service=None):

    def _serialize(t, include_relations=True):
        data = {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'user_id': t.user_id,
            'category_id': t.category_id,
            'created_at': str(t.created_at),
            'updated_at': str(t.updated_at),
            'due_date': str(t.due_date) if t.due_date else None,
            'tags': t.tags.split(',') if t.tags else [],
            'overdue': t.is_overdue(),
        }
        if include_relations:
            data['user_name'] = t.user.name if t.user else None
            data['category_name'] = t.category.name if t.category else None
        return data

    def get_all():
        tasks = Task.query.options(
            joinedload(Task.user),
            joinedload(Task.category),
        ).all()
        return [_serialize(t) for t in tasks]

    def get_one(task_id):
        task = db.session.get(Task, task_id)
        if not task:
            raise AppError('Task não encontrada', 404)
        return _serialize(task)

    def create(data):
        if not data:
            raise AppError('Dados inválidos')

        title = data.get('title')
        if not title:
            raise AppError('Título é obrigatório')
        if len(title) < 3:
            raise AppError('Título muito curto')
        if len(title) > 200:
            raise AppError('Título muito longo')

        status = data.get('status', 'pending')
        if status not in ('pending', 'in_progress', 'done', 'cancelled'):
            raise AppError('Status inválido')

        priority = data.get('priority', 3)
        if priority < 1 or priority > 5:
            raise AppError('Prioridade deve ser entre 1 e 5')

        user_id = data.get('user_id')
        user = None
        if user_id:
            user = db.session.get(User, user_id)
            if not user:
                raise AppError('Usuário não encontrado', 404)

        category_id = data.get('category_id')
        if category_id:
            if not db.session.get(Category, category_id):
                raise AppError('Categoria não encontrada', 404)

        task = Task()
        task.title = title
        task.description = data.get('description', '')
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id

        due_date = data.get('due_date')
        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                raise AppError('Formato de data inválido. Use YYYY-MM-DD')

        tags = data.get('tags')
        if tags:
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        db.session.add(task)
        db.session.commit()

        if user and notification_service:
            notification_service.notify_task_assigned(user, task)

        return _serialize(task, include_relations=False), 201

    def update(task_id, data):
        task = db.session.get(Task, task_id)
        if not task:
            raise AppError('Task não encontrada', 404)
        if not data:
            raise AppError('Dados inválidos')

        if 'title' in data:
            if len(data['title']) < 3:
                raise AppError('Título muito curto')
            if len(data['title']) > 200:
                raise AppError('Título muito longo')
            task.title = data['title']

        if 'description' in data:
            task.description = data['description']

        if 'status' in data:
            if data['status'] not in ('pending', 'in_progress', 'done', 'cancelled'):
                raise AppError('Status inválido')
            task.status = data['status']

        if 'priority' in data:
            if data['priority'] < 1 or data['priority'] > 5:
                raise AppError('Prioridade deve ser entre 1 e 5')
            task.priority = data['priority']

        if 'user_id' in data:
            if data['user_id'] and not db.session.get(User, data['user_id']):
                raise AppError('Usuário não encontrado', 404)
            task.user_id = data['user_id']

        if 'category_id' in data:
            if data['category_id'] and not db.session.get(Category, data['category_id']):
                raise AppError('Categoria não encontrada', 404)
            task.category_id = data['category_id']

        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except ValueError:
                    raise AppError('Formato de data inválido')
            else:
                task.due_date = None

        if 'tags' in data:
            task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

        task.updated_at = datetime.utcnow()
        db.session.commit()
        return _serialize(task, include_relations=False)

    def delete(task_id):
        task = db.session.get(Task, task_id)
        if not task:
            raise AppError('Task não encontrada', 404)
        db.session.delete(task)
        db.session.commit()

    def search(q='', status='', priority='', user_id=''):
        query = Task.query
        if q:
            query = query.filter(
                db.or_(Task.title.like(f'%{q}%'), Task.description.like(f'%{q}%'))
            )
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == int(priority))
        if user_id:
            query = query.filter(Task.user_id == int(user_id))
        return [t.to_dict() for t in query.all()]

    def stats():
        total = Task.query.count()
        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()
        overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())
        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
            'overdue': overdue_count,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        }

    return {
        'get_all': get_all,
        'get_one': get_one,
        'create': create,
        'update': update,
        'delete': delete,
        'search': search,
        'stats': stats,
    }
