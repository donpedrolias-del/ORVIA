"""
Coder Agent - Génère le code pour chaque étape
Version améliorée avec génération automatique du frontend
"""

import os

class Coder:
    def __init__(self):
        self.output_dir = "generated_project"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_code(self, step, plan):
        """Génère le code pour une étape spécifique"""
        
        step_name = step['name']
        
        try:
            if "Initialiser la structure de l'API" in step_name:
                return self._init_api_structure()
            elif "Créer les endpoints de base" in step_name:
                return self._add_endpoints()
            elif "Ajouter la gestion des utilisateurs" in step_name:
                return self._add_user_crud()
            elif "Ajouter la documentation" in step_name:
                return self._add_readme()
            else:
                return True, "Étape générique"
        except Exception as e:
            return False, str(e)
    
    def _init_api_structure(self):
        """Crée la structure de base de l'API ET le frontend"""
        
        # ========== BACKEND ==========
        filepath = os.path.join(self.output_dir, "backend.py")
        
        backend_code = '''from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

users_db = {}
counter = 1

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"users": list(users_db.values()), "total": len(users_db)})

@app.route('/api/create_user', methods=['POST'])
def create_user():
    global counter
    data = request.get_json()
    user_id = counter
    counter += 1
    users_db[user_id] = {
        "id": user_id,
        "name": data.get('name'),
        "email": data.get('email'),
        "created_at": datetime.now().isoformat()
    }
    return jsonify({"message": "Utilisateur créé", "user": users_db[user_id]}), 201

@app.route('/api/user/<int:user_id>', methods=['GET', 'DELETE'])
def manage_user(user_id):
    if user_id not in users_db:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    if request.method == 'GET':
        return jsonify({"user": users_db[user_id]})
    elif request.method == 'DELETE':
        deleted = users_db.pop(user_id)
        return jsonify({"message": "Utilisateur supprimé", "user": deleted})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"\\n🚀 API sur http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
'''
        
        with open(filepath, 'w') as f:
            f.write(backend_code)
        
        # ========== FRONTEND ==========
        html_path = os.path.join(self.output_dir, "index.html")
        
        html_code = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI BUILDER - Application Générée</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { color: #667eea; margin-bottom: 10px; }
        h2 { color: #667eea; margin-bottom: 20px; font-size: 1.5rem; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 500; }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        input:focus { outline: none; border-color: #667eea; }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover { background: #764ba2; transform: translateY(-2px); }
        .delete-btn { background: #dc3545; padding: 6px 12px; font-size: 14px; }
        .delete-btn:hover { background: #c82333; }
        .user-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .user-info h3 { margin-bottom: 5px; }
        .user-info p { color: #666; font-size: 14px; }
        .stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 15px;
            flex: 1;
            text-align: center;
        }
        .stat-card h3 { font-size: 2rem; margin-bottom: 5px; }
        .empty { text-align: center; color: #999; padding: 40px; }
        .status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🤖 AI BUILDER</h1>
            <p>Application générée automatiquement</p>
        </div>
        
        <div class="card">
            <h2>➕ Ajouter un utilisateur</h2>
            <div class="form-group">
                <label>Nom complet</label>
                <input type="text" id="name" placeholder="Ex: Jean Dupont">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="email" placeholder="Ex: jean@email.com">
            </div>
            <button onclick="createUser()">Créer l'utilisateur</button>
        </div>
        
        <div class="card">
            <h2>📋 Liste des utilisateurs</h2>
            <div class="stats">
                <div class="stat-card">
                    <h3 id="totalUsers">0</h3>
                    <p>Utilisateurs</p>
                </div>
                <div class="stat-card">
                    <h3 id="apiStatus">...</h3>
                    <p>Statut API</p>
                </div>
            </div>
            <div id="usersList">
                <div class="empty">Chargement...</div>
            </div>
        </div>
    </div>
    
    <script>
        const API_URL = 'http://127.0.0.1:5002';
        
        async function checkAPI() {
            try {
                const response = await fetch(`${API_URL}/api/status`);
                document.getElementById('apiStatus').textContent = '✅ Online';
                return true;
            } catch (error) {
                document.getElementById('apiStatus').textContent = '❌ Offline';
                return false;
            }
        }
        
        async function loadUsers() {
            try {
                const response = await fetch(`${API_URL}/api/users`);
                const data = await response.json();
                displayUsers(data.users);
                document.getElementById('totalUsers').textContent = data.total;
            } catch (error) {
                console.error('Erreur:', error);
            }
        }
        
        function displayUsers(users) {
            const container = document.getElementById('usersList');
            if (users.length === 0) {
                container.innerHTML = '<div class="empty">📭 Aucun utilisateur. Ajoutez-en un !</div>';
                return;
            }
            container.innerHTML = users.map(user => `
                <div class="user-card">
                    <div class="user-info">
                        <h3>#${user.id} ${user.name}</h3>
                        <p>✉️ ${user.email}</p>
                    </div>
                    <button class="delete-btn" onclick="deleteUser(${user.id})">🗑️ Supprimer</button>
                </div>
            `).join('');
        }
        
        async function createUser() {
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            if (!name || !email) {
                alert('Veuillez remplir tous les champs');
                return;
            }
            try {
                const response = await fetch(`${API_URL}/api/create_user`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email })
                });
                if (response.ok) {
                    document.getElementById('name').value = '';
                    document.getElementById('email').value = '';
                    loadUsers();
                }
            } catch (error) {
                alert('Erreur de connexion');
            }
        }
        
        async function deleteUser(id) {
            if (!confirm('Supprimer cet utilisateur ?')) return;
            try {
                await fetch(`${API_URL}/api/user/${id}`, { method: 'DELETE' });
                loadUsers();
            } catch (error) {
                alert('Erreur');
            }
        }
        
        checkAPI();
        loadUsers();
        setInterval(() => { checkAPI(); loadUsers(); }, 5000);
    </script>
</body>
</html>
'''
        
        with open(html_path, 'w') as f:
            f.write(html_code)
        
        # ========== REQUIREMENTS ==========
        req_path = os.path.join(self.output_dir, "requirements.txt")
        with open(req_path, 'w') as f:
            f.write("Flask==2.3.2\nflask-cors==4.0.0\n")
        
        return True, {"backend.py": "créé", "index.html": "créé", "requirements.txt": "créé"}
    
    def _add_endpoints(self):
        """Ajoute les endpoints (déjà inclus dans init)"""
        return True, "Endpoints déjà présents"
    
    def _add_user_crud(self):
        """Ajoute le CRUD (déjà inclus dans init)"""
        return True, "CRUD déjà présent"
    
    def _add_readme(self):
        """Ajoute le README"""
        readme_path = os.path.join(self.output_dir, "README.md")
        readme = '''# Application générée par AI BUILDER

## Installation
```bash
pip install -r requirements.txt
