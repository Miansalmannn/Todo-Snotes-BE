from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Todo, User
from datetime import datetime
import pytz

main_bp = Blueprint('main', __name__)


def convert_to_local_time(date: datetime, timezone: str = "Asia/Karachi"):
    if not date:
        return None

    utc_timezone = pytz.utc  
    if date.tzinfo is None:
        date = utc_timezone.localize(date)
    else:
        date = date.astimezone(utc_timezone)
    as_date_time = date
    return as_date_time

def format_date_with_suffix(date: datetime):
    if not date:
        return None
    day = date.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return date.strftime(f"%a, %d {suffix} %b %Y %I:%M %p")

original_time = datetime(2025, 8, 6, 14, 17)
local_time = convert_to_local_time(original_time)  
formatted_time = format_date_with_suffix(local_time)  

print(f"Local time: {local_time}")
print(f"Formatted time: {formatted_time}")


def serialize_todo(todo: Todo):
    local_time = convert_to_local_time(todo.created_at)
    formatted_time = format_date_with_suffix(local_time)

    return {
        "id": todo.id,
        "title": todo.title,
        "completed": todo.completed,
        "createdAt": formatted_time,
    }


@main_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
    })


@main_bp.route('/todos', methods=['GET', 'POST'])
@jwt_required()
def handle_todos():
    user_id = get_jwt_identity()

    if request.method == 'GET':
        user = User.query.get(user_id)
        todos = Todo.query.filter_by(user_id=user_id).order_by(Todo.created_at.desc()).all()

        return jsonify({
            "username": user.username,
            "todos": [serialize_todo(t) for t in todos]
        })

    if request.method == 'POST':
        data = request.get_json(silent=True)
        if not data or 'title' not in data:
            return jsonify({'message': 'Title is required'}), 400

        todo = Todo(title=data['title'], user_id=user_id)
        db.session.add(todo)
        db.session.commit()

        return jsonify(serialize_todo(todo)), 201


@main_bp.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()

    if not todo:
        return jsonify({'message': 'Todo not found'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'message': 'Invalid request'}), 400

    todo.title = data.get('title', todo.title)
    todo.completed = data.get('completed', todo.completed)
    db.session.commit()

    return jsonify(serialize_todo(todo))


@main_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()

    if not todo:
        return jsonify({'message': 'Todo not found'}), 404

    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Todo deleted'})

@main_bp.route('/todos', methods=['DELETE'])
@jwt_required()
def delete_all_todos():
    user_id = get_jwt_identity()
    todos = Todo.query.filter_by(user_id=user_id).all()

    if not todos:
        return jsonify({'message': 'No todos found'}), 404

    for todo in todos:
        db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'All todos deleted'})
