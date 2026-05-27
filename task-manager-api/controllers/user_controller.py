import re
from database import db
from models.user import User
from models.task import Task
from middlewares.error_handler import AppError

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def build_user_controller():

    def get_all():
        users = User.query.all()
        return [
            {**u.to_public(), 'task_count': len(u.tasks)}
            for u in users
        ]

    def get_one(user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        data = user.to_public()
        data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
        return data

    def create(data):
        if not data:
            raise AppError('Dados inválidos')

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not name:
            raise AppError('Nome é obrigatório')
        if not email:
            raise AppError('Email é obrigatório')
        if not password:
            raise AppError('Senha é obrigatória')
        if not _EMAIL_RE.match(email):
            raise AppError('Email inválido')
        if len(password) < 4:
            raise AppError('Senha deve ter no mínimo 4 caracteres')
        if User.query.filter_by(email=email).first():
            raise AppError('Email já cadastrado', 409)
        if role not in ('user', 'admin', 'manager'):
            raise AppError('Role inválido')

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        db.session.add(user)
        db.session.commit()
        return user.to_public(), 201

    def update(user_id, data):
        user = db.session.get(User, user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        if not data:
            raise AppError('Dados inválidos')

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not _EMAIL_RE.match(data['email']):
                raise AppError('Email inválido')
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise AppError('Email já cadastrado', 409)
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < 4:
                raise AppError('Senha muito curta')
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in ('user', 'admin', 'manager'):
                raise AppError('Role inválido')
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        db.session.commit()
        return user.to_public()

    def delete(user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        Task.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()

    def login(data):
        if not data:
            raise AppError('Dados inválidos')

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise AppError('Email e senha são obrigatórios')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise AppError('Credenciais inválidas', 401)
        if not user.active:
            raise AppError('Usuário inativo', 403)

        return {'message': 'Login realizado com sucesso', 'user': user.to_public()}

    def get_user_tasks(user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)
        tasks = Task.query.filter_by(user_id=user_id).all()
        result = []
        for t in tasks:
            d = {
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'created_at': str(t.created_at),
                'due_date': str(t.due_date) if t.due_date else None,
                'overdue': t.is_overdue(),
            }
            result.append(d)
        return result

    return {
        'get_all': get_all,
        'get_one': get_one,
        'create': create,
        'update': update,
        'delete': delete,
        'login': login,
        'get_user_tasks': get_user_tasks,
    }
