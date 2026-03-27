"""
Coder Agent PRO - ARTISAN PRO
Génère des applications professionnelles avec authentification et base de données
"""

import os

class CoderPro:
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
        
        # BACKEND AVEC AUTHENTIFICATION JWT
        backend_code = '''"""
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
    print(f"\\n🚀 API PRO sur http://localhost:{port}")
    print("👤 Compte démo: demo / demo123")
    app.run(host='0.0.0.0', port=port, debug=True)'''
        
        with open(os.path.join(self.output_dir, "backend.py"), 'w') as f:
            f.write(backend_code)
        
        with open(os.path.join(self.output_dir, "requirements.txt"), 'w') as f:
            f.write("Flask==2.3.2\nflask-cors==4.0.0\nflask-sqlalchemy==3.1.1\nflask-jwt-extended==4.5.2\n")
        
        # FRONTEND AVEC 3 PAGES
        frontend_code = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORVIA - {idea[:40]}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        .logo {{
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .nav-links {{
            display: flex;
            gap: 2rem;
        }}
        .nav-links a {{
            text-decoration: none;
            color: #333;
            font-weight: 500;
            cursor: pointer;
        }}
        .nav-links a:hover {{ color: #667eea; }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }}
        .page {{ display: none; animation: fadeIn 0.5s ease; }}
        .page.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .card {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #667eea; margin-bottom: 1rem; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem;
            border-radius: 20px;
            text-align: center;
        }}
        .stat-card h3 {{ font-size: 2rem; }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
        }}
        .login-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 2rem;
        }}
        .login-card {{
            background: white;
            border-radius: 30px;
            padding: 2rem;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }}
        .hidden {{ display: none; }}
        .btn-logout {{
            background: #dc3545;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            cursor: pointer;
        }}
        input, textarea {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            margin: 0.5rem 0;
            font-size: 1rem;
        }}
        @media (max-width: 768px) {{
            .nav-container {{ flex-direction: column; gap: 1rem; }}
            .nav-links {{ gap: 1rem; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div id="loginView" class="login-container">
        <div class="login-card">
            <h1>🔐 ORVIA PRO</h1>
            <input type="text" id="loginUsername" placeholder="demo">
            <input type="password" id="loginPassword" placeholder="demo123">
            <button class="btn-primary" style="width:100%" onclick="login()">Se connecter</button>
            <p style="margin-top:1rem; text-align:center;">demo / demo123</p>
            <div id="loginError" style="color:red; margin-top:1rem;"></div>
        </div>
    </div>

    <div id="appView" class="hidden">
        <div class="navbar">
            <div class="nav-container">
                <div class="logo">⚡ {idea[:30]}</div>
                <div class="nav-links">
                    <a onclick="showPage('accueil')">🏠 Accueil</a>
                    <a onclick="showPage('information')">ℹ️ Information</a>
                    <a onclick="showPage('developpement')">🚀 Développement</a>
                </div>
                <button class="btn-logout" onclick="logout()">Déconnexion</button>
            </div>
        </div>
        
        <div class="container">
            <div id="accueil" class="page active">
                <div class="card"><h1>🏠 Bienvenue</h1><p>{idea[:100]}</p></div>
                <div class="stats-grid">
                    <div class="stat-card"><h3 id="totalCount">0</h3><p>Total</p></div>
                    <div class="stat-card"><h3 id="completedCount">0</h3><p>Terminés</p></div>
                    <div class="stat-card"><h3 id="completionRate">0%</h3><p>Progression</p></div>
                </div>
                <div class="card">
                    <h2>➕ Ajouter</h2>
                    <input type="text" id="itemTitle" placeholder="Titre">
                    <textarea id="itemDesc" rows="2" placeholder="Description"></textarea>
                    <button class="btn-primary" onclick="createItem()">Ajouter</button>
                </div>
                <div class="card">
                    <h2>📋 Liste</h2>
                    <div id="itemsList"></div>
                </div>
            </div>
            <div id="information" class="page">
                <div class="card">
                    <h1>ℹ️ À propos</h1>
                    <p>Application générée par ORVIA PRO</p>
                    <h3>✨ Fonctionnalités</h3>
                    <ul style="margin-left: 2rem;"><li>✅ Authentification JWT</li><li>✅ Base de données SQLite</li><li>✅ Interface responsive</li><li>✅ 3 pages (Accueil, Info, Dev)</li></ul>
                </div>
            </div>
            <div id="developpement" class="page">
                <div class="card">
                    <h1>🚀 Technologies</h1>
                    <ul style="margin-left: 2rem;">
                        <li>🐍 Python / Flask</li>
                        <li>🗄️ SQLAlchemy / SQLite</li>
                        <li>🔐 JWT pour l'authentification</li>
                        <li>🎨 HTML5 / CSS3 / JavaScript</li>
                        <li>📱 Design responsive</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_URL = 'http://127.0.0.1:5002';
        let token = localStorage.getItem('token');
        
        function showPage(id) {{
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(id).classList.add('active');
        }}
        
        async function login() {{
            const u = document.getElementById('loginUsername').value;
            const p = document.getElementById('loginPassword').value;
            try {{
                const res = await fetch(API_URL + '/api/auth/login', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ username: u, password: p }})
                }});
                const data = await res.json();
                if (res.ok) {{
                    token = data.token;
                    localStorage.setItem('token', token);
                    document.getElementById('loginView').classList.add('hidden');
                    document.getElementById('appView').classList.remove('hidden');
                    loadItems();
                    loadStats();
                }} else {{
                    document.getElementById('loginError').textContent = data.error;
                }}
            }} catch(e) {{
                document.getElementById('loginError').textContent = 'Erreur de connexion';
            }}
        }}
        
        function logout() {{
            token = null;
            localStorage.removeItem('token');
            document.getElementById('loginView').classList.remove('hidden');
            document.getElementById('appView').classList.add('hidden');
        }}
        
        async function loadItems() {{
            if (!token) return;
            try {{
                const res = await fetch(API_URL + '/api/items', {{
                    headers: {{ 'Authorization': 'Bearer ' + token }}
                }});
                const data = await res.json();
                const container = document.getElementById('itemsList');
                if (data.items.length === 0) {{
                    container.innerHTML = '<p style="text-align:center; color:#999;">📭 Aucun élément</p>';
                    return;
                }}
                container.innerHTML = data.items.slice(0, 5).map(item => `
                    <div style="background:#f8f9fa; border-radius:12px; padding:1rem; margin-bottom:0.5rem;">
                        <strong>${escapeHtml(item.title)}</strong><br>
                        <small>${escapeHtml(item.description || '')}</small>
                    </div>
                `).join('');
            }} catch(e) {{ console.error(e); }}
        }}
        
        async function createItem() {{
            const title = document.getElementById('itemTitle').value;
            const description = document.getElementById('itemDesc').value;
            if (!title) return alert('Entrez un titre');
            try {{
                await fetch(API_URL + '/api/items', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token }},
                    body: JSON.stringify({{ title, description }})
                }});
                document.getElementById('itemTitle').value = '';
                document.getElementById('itemDesc').value = '';
                loadItems();
                loadStats();
            }} catch(e) {{ alert('Erreur'); }}
        }}
        
        async function loadStats() {{
            if (!token) return;
            try {{
                const res = await fetch(API_URL + '/api/stats', {{
                    headers: {{ 'Authorization': 'Bearer ' + token }}
                }});
                const data = await res.json();
                document.getElementById('totalCount').textContent = data.total;
                document.getElementById('completedCount').textContent = data.completed;
                document.getElementById('completionRate').textContent = data.completion_rate + '%';
            }} catch(e) {{ console.error(e); }}
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        if (token) {{ loadItems(); loadStats(); }}
    </script>
</body>
</html>'''
        
        with open(os.path.join(self.output_dir, "index.html"), 'w') as f:
            f.write(frontend_code)
        
        return True, "Application professionnelle créée avec succès"
