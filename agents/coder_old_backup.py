"""
Coder Agent - ARTISAN PRO
Génère des applications professionnelles avec authentification, base de données et design moderne
"""

import os

class Coder:
    def __init__(self):
        self.output_dir = "generated_project"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_code(self, step, plan):
        try:
            return self._create_pro_app(plan)
        except Exception as e:
            return False, str(e)
    
    def _create_pro_app(self, plan):
        idea = plan['idea']
        project_type = plan.get('project_type', 'generic')
        
        # ========== BACKEND AVEC AUTH ET BASE DE DONNÉES ==========
        backend_code = '''"""
Application professionnelle générée par ORVIA
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

# Configuration
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# ========== MODÈLES ==========
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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Créer la base de données et utilisateur démo
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='demo').first():
        demo_user = User(username='demo', email='demo@orvia.com', password='demo123')
        db.session.add(demo_user)
        db.session.commit()
        print("✅ Compte démo créé: demo / demo123")

# ========== ROUTES AUTH ==========
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Utilisateur existe déjà"}), 400
    user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Utilisateur créé", "user": {"id": user.id, "username": user.username}}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if not user:
        return jsonify({"error": "Identifiants invalides"}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token, "user": {"id": user.id, "username": user.username}}), 200

# ========== ROUTES PRINCIPALES ==========
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat(), "version": "2.0"})

@app.route('/api/items', methods=['GET'])
@jwt_required()
def get_items():
    user_id = get_jwt_identity()
    category = request.args.get('category')
    search = request.args.get('search')
    query = Item.query.filter_by(user_id=user_id)
    if category and category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Item.title.contains(search) | Item.description.contains(search))
    items = query.order_by(Item.priority.desc(), Item.created_at.desc()).all()
    return jsonify({
        "items": [{
            "id": i.id, "title": i.title, "description": i.description,
            "category": i.category, "completed": i.completed, "priority": i.priority,
            "created_at": i.created_at.isoformat()
        } for i in items],
        "total": len(items)
    })

@app.route('/api/items', methods=['POST'])
@jwt_required()
def create_item():
    user_id = get_jwt_identity()
    data = request.get_json()
    item = Item(
        title=data['title'], description=data.get('description', ''),
        category=data.get('category', 'general'), priority=data.get('priority', 1),
        user_id=user_id
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Créé", "item": {"id": item.id}}), 201

@app.route('/api/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    user_id = get_jwt_identity()
    item = Item.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "Non trouvé"}), 404
    data = request.get_json()
    if 'title' in data:
        item.title = data['title']
    if 'description' in data:
        item.description = data['description']
    if 'category' in data:
        item.category = data['category']
    if 'completed' in data:
        item.completed = data['completed']
    if 'priority' in data:
        item.priority = data['priority']
    item.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Mis à jour"}), 200

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    user_id = get_jwt_identity()
    item = Item.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "Non trouvé"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Supprimé"}), 200

@app.route('/api/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    total = Item.query.filter_by(user_id=user_id).count()
    completed = Item.query.filter_by(user_id=user_id, completed=True).count()
    return jsonify({
        "total": total, "completed": completed, "pending": total - completed,
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 1)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"\\n🚀 API Pro démarrée sur http://localhost:{port}")
    print("👤 Compte démo: demo / demo123")
    app.run(host='0.0.0.0', port=port, debug=True)
'''
        
        with open(os.path.join(self.output_dir, "backend.py"), 'w') as f:
            f.write(backend_code)
        
        # ========== REQUIREMENTS ==========
        with open(os.path.join(self.output_dir, "requirements.txt"), 'w') as f:
            f.write("Flask==2.3.2\nflask-cors==4.0.0\nflask-sqlalchemy==3.1.1\nflask-jwt-extended==4.5.2\n")
        
        # ========== FRONTEND PRO ==========
        html_code = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORVIA Pro - Application</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .user-info { display: flex; align-items: center; gap: 1rem; }
        .btn-logout {
            background: #dc3545;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            cursor: pointer;
        }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem;
            border-radius: 20px;
            text-align: center;
        }
        .stat-card h3 { font-size: 2rem; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #333; }
        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .btn-primary:hover { transform: translateY(-2px); }
        .items-grid { display: grid; gap: 1rem; }
        .item-card {
            background: #f8f9fa;
            border-radius: 16px;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }
        .item-card:hover { transform: translateX(5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .item-content { flex: 1; }
        .item-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem; }
        .item-meta { font-size: 0.8rem; color: #666; }
        .item-actions { display: flex; gap: 0.5rem; }
        .btn-icon {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 50%;
            transition: all 0.2s;
        }
        .btn-icon:hover { background: rgba(0,0,0,0.1); }
        .priority-high { border-left: 4px solid #dc3545; }
        .priority-medium { border-left: 4px solid #ffc107; }
        .priority-low { border-left: 4px solid #28a745; }
        .completed { opacity: 0.6; text-decoration: line-through; }
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 2rem;
        }
        .login-card {
            background: white;
            border-radius: 30px;
            padding: 2rem;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        .hidden { display: none; }
        @media (max-width: 768px) {
            .container { padding: 0 1rem; }
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div id="loginView" class="login-container">
        <div class="login-card">
            <h1 style="margin-bottom: 2rem;">🔐 ORVIA Pro</h1>
            <div class="form-group">
                <label>Nom d'utilisateur</label>
                <input type="text" id="loginUsername" placeholder="demo">
            </div>
            <div class="form-group">
                <label>Mot de passe</label>
                <input type="password" id="loginPassword" placeholder="demo123">
            </div>
            <button class="btn-primary" style="width:100%" onclick="login()">Se connecter</button>
            <p style="margin-top: 1rem; text-align:center; color:#666;">Compte démo: demo / demo123</p>
            <div id="loginError" style="color:red; margin-top:1rem; text-align:center;"></div>
        </div>
    </div>

    <div id="appView" class="hidden">
        <div class="navbar">
            <div class="nav-container">
                <div class="logo">⚡ ORVIA Pro</div>
                <div class="user-info">
                    <span id="username"></span>
                    <button class="btn-logout" onclick="logout()">Déconnexion</button>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="stats-grid" id="stats">
                <div class="stat-card"><h3 id="totalCount">0</h3><p>Total</p></div>
                <div class="stat-card"><h3 id="completedCount">0</h3><p>Terminés</p></div>
                <div class="stat-card"><h3 id="pendingCount">0</h3><p>En cours</p></div>
                <div class="stat-card"><h3 id="completionRate">0%</h3><p>Progression</p></div>
            </div>
            
            <div class="card">
                <h2 style="margin-bottom: 1rem;">➕ Ajouter un élément</h2>
                <div class="form-group"><input type="text" id="itemTitle" placeholder="Titre..."></div>
                <div class="form-group"><textarea id="itemDesc" rows="2" placeholder="Description..."></textarea></div>
                <div class="form-group">
                    <select id="itemCategory">
                        <option value="general">📋 Général</option>
                        <option value="work">💼 Travail</option>
                        <option value="personal">🏠 Personnel</option>
                        <option value="urgent">🔥 Urgent</option>
                    </select>
                </div>
                <div class="form-group">
                    <select id="itemPriority">
                        <option value="1">⭐ Priorité basse</option>
                        <option value="2">⭐⭐ Priorité moyenne</option>
                        <option value="3">⭐⭐⭐ Priorité haute</option>
                    </select>
                </div>
                <button class="btn-primary" onclick="createItem()">✨ Ajouter</button>
            </div>
            
            <div class="card">
                <h2 style="margin-bottom: 1rem;">📋 Liste des éléments</h2>
                <div class="form-group"><input type="text" id="searchInput" placeholder="🔍 Rechercher..." onkeyup="loadItems()"></div>
                <div class="form-group">
                    <select id="filterCategory" onchange="loadItems()">
                        <option value="all">Toutes catégories</option>
                        <option value="general">📋 Général</option>
                        <option value="work">💼 Travail</option>
                        <option value="personal">🏠 Personnel</option>
                        <option value="urgent">🔥 Urgent</option>
                    </select>
                </div>
                <div id="itemsList" class="items-grid"></div>
            </div>
        </div>
    </div>

    <script>
        const API_URL = 'http://127.0.0.1:5002';
        let token = localStorage.getItem('token');
        
        async function login() {
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            try {
                const res = await fetch(API_URL + '/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                if (res.ok) {
                    token = data.token;
                    localStorage.setItem('token', token);
                    showApp();
                    loadItems();
                    loadStats();
                } else {
                    document.getElementById('loginError').textContent = data.error;
                }
            } catch(e) { document.getElementById('loginError').textContent = 'Erreur de connexion'; }
        }
        
        function logout() { token = null; localStorage.removeItem('token'); showLogin(); }
        function showApp() { document.getElementById('loginView').classList.add('hidden'); document.getElementById('appView').classList.remove('hidden'); }
        function showLogin() { document.getElementById('loginView').classList.remove('hidden'); document.getElementById('appView').classList.add('hidden'); }
        
        async function loadItems() {
            if (!token) return;
            const search = document.getElementById('searchInput').value;
            const category = document.getElementById('filterCategory').value;
            try {
                const res = await fetch(API_URL + '/api/items?search=' + search + '&category=' + category, {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                const data = await res.json();
                renderItems(data.items);
            } catch(e) { console.error(e); }
        }
        
        function renderItems(items) {
            const container = document.getElementById('itemsList');
            if (items.length === 0) { container.innerHTML = '<div style="text-align:center; padding:2rem; color:#999;">📭 Aucun élément</div>'; return; }
            container.innerHTML = items.map(item => `
                <div class="item-card priority-${item.priority === 3 ? 'high' : (item.priority === 2 ? 'medium' : 'low')} ${item.completed ? 'completed' : ''}">
                    <div class="item-content">
                        <div class="item-title">${escapeHtml(item.title)}</div>
                        <div class="item-meta">${item.description || ''} • ${item.category} • 📅 ${new Date(item.created_at).toLocaleDateString()}</div>
                    </div>
                    <div class="item-actions">
                        <button class="btn-icon" onclick="toggleComplete(${item.id}, ${!item.completed})">${item.completed ? '↩️' : '✅'}</button>
                        <button class="btn-icon" onclick="deleteItem(${item.id})">🗑️</button>
                    </div>
                </div>
            `).join('');
        }
        
        async function createItem() {
            const title = document.getElementById('itemTitle').value;
            const description = document.getElementById('itemDesc').value;
            const category = document.getElementById('itemCategory').value;
            const priority = parseInt(document.getElementById('itemPriority').value);
            if (!title) return alert('Entrez un titre');
            try {
                const res = await fetch(API_URL + '/api/items', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                    body: JSON.stringify({ title, description, category, priority })
                });
                if (res.ok) {
                    document.getElementById('itemTitle').value = '';
                    document.getElementById('itemDesc').value = '';
                    loadItems();
                    loadStats();
                }
            } catch(e) { alert('Erreur'); }
        }
        
        async function toggleComplete(id, completed) {
            try {
                await fetch(API_URL + '/api/items/' + id, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                    body: JSON.stringify({ completed })
                });
                loadItems();
                loadStats();
            } catch(e) { console.error(e); }
        }
        
        async function deleteItem(id) {
            if (!confirm('Supprimer ?')) return;
            try {
                await fetch(API_URL + '/api/items/' + id, {
                    method: 'DELETE',
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                loadItems();
                loadStats();
            } catch(e) { console.error(e); }
        }
        
        async function loadStats() {
            if (!token) return;
            try {
                const res = await fetch(API_URL + '/api/stats', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                const data = await res.json();
                document.getElementById('totalCount').textContent = data.total;
                document.getElementById('completedCount').textContent = data.completed;
                document.getElementById('pendingCount').textContent = data.pending;
                document.getElementById('completionRate').textContent = data.completion_rate + '%';
            } catch(e) { console.error(e); }
        }
        
        function escapeHtml(text) { const d=document.createElement('div'); d.textContent=text; return d.innerHTML; }
        
        if (token) { showApp(); loadItems(); loadStats(); }
    </script>
</body>
</html>'''
        
        with open(os.path.join(self.output_dir, "index.html"), 'w') as f:
            f.write(html_code)
        
        return True, "Application professionnelle créée avec authentification"
