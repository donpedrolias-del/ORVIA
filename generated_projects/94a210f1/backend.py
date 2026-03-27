"""
Application professionnelle générée par ORVIA PRO
Avec authentification JWT et base de données SQLite
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import secrets

app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='demo').first():
        demo_user = User(username='demo', email='demo@orvia.com', password='demo123')
        db.session.add(demo_user)
        db.session.commit()

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Utilisateur existe déjà"}), 400
    user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Utilisateur créé"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if not user:
        return jsonify({"error": "Identifiants invalides"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": {"id": user.id, "username": user.username}}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/items', methods=['GET'])
@jwt_required()
def get_items():
    user_id = get_jwt_identity()
    items = Item.query.filter_by(user_id=user_id).order_by(Item.created_at.desc()).all()
    return jsonify({
        "items": [{"id": i.id, "title": i.title, "description": i.description,
                   "category": i.category, "completed": i.completed, "priority": i.priority,
                   "created_at": i.created_at.isoformat()} for i in items],
        "total": len(items)
    })

@app.route('/api/items', methods=['POST'])
@jwt_required()
def create_item():
    user_id = get_jwt_identity()
    data = request.get_json()
    item = Item(title=data['title'], description=data.get('description', ''),
                category=data.get('category', 'general'), priority=data.get('priority', 1),
                user_id=user_id)
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Créé", "id": item.id}), 201

@app.route('/api/items/<int:item_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_item(item_id):
    user_id = get_jwt_identity()
    item = Item.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "Non trouvé"}), 404
    if request.method == 'PUT':
        data = request.get_json()
        if 'title' in data: item.title = data['title']
        if 'description' in data: item.description = data['description']
        if 'completed' in data: item.completed = data['completed']
        db.session.commit()
        return jsonify({"message": "Mis à jour"}), 200
    else:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Supprimé"}), 200

@app.route('/api/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    total = Item.query.filter_by(user_id=user_id).count()
    completed = Item.query.filter_by(user_id=user_id, completed=True).count()
    return jsonify({"total": total, "completed": completed,
                    "completion_rate": round((completed / total * 100) if total > 0 else 0, 1)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"\n🚀 API PRO sur http://localhost:{port}")
    print("👤 Compte démo: demo / demo123")
    app.run(host='0.0.0.0', port=port, debug=True)