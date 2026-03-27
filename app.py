"""
ORVIA - API principale
Expose les agents via des endpoints REST
"""

import sys
import os

# Ajouter le dossier courant au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import uuid
import shutil
import zipfile
from io import BytesIO
from datetime import datetime
import traceback

# Import des agents
try:
    from agents.planner import Planner
    from agents.coder import Coder
    from agents.designer import Designer
    from agents.debugger import Debugger
    from agents.tester import Tester
    from agents.memory import Memory
    print("✅ Agents importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("📁 Dossier courant:", os.getcwd())
    print("📁 Contenu du dossier agents:", os.listdir('agents') if os.path.exists('agents') else "dossier agents manquant")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Initialisation des agents
planner = Planner()
coder = Coder()
designer = Designer()
debugger = Debugger()
tester = Tester()
memory = Memory()

# Dossiers
PROJECTS_DIR = "generated_projects"
TEMP_DIR = "generated_project"
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# ========== ROUTES ==========

@app.route('/')
def home():
    return jsonify({
        "name": "ORVIA API",
        "version": "2.0",
        "status": "online",
        "agents": ["vision", "artisan", "sentinel", "judge", "designer", "memoire"]
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    idea = data.get('idea', '')
    
    if not idea:
        return jsonify({"error": "Aucune idée fournie"}), 400
    
    print(f"🚀 Génération pour : {idea}")
    
    try:
        # 1. Planner crée le plan
        plan = planner.create_plan(idea)
        
        # 2. Coder génère le code
        success, message = coder.generate_code(None, plan)
        
        if not success:
            return jsonify({"error": message}), 500
        
        # 3. Créer le dossier du projet
        project_id = plan['id']
        project_path = os.path.join(PROJECTS_DIR, project_id)
        os.makedirs(project_path, exist_ok=True)
        
        # 4. Déplacer les fichiers
        if os.path.exists(TEMP_DIR):
            for file in os.listdir(TEMP_DIR):
                src = os.path.join(TEMP_DIR, file)
                dst = os.path.join(project_path, file)
                if os.path.isfile(src):
                    shutil.move(src, dst)
        
        # 5. Sauvegarder le plan
        with open(os.path.join(project_path, "plan.json"), 'w') as f:
            json.dump(plan, f, indent=2)
        
        # 6. Designer améliore l'interface
        html_path = os.path.join(project_path, "index.html")
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            if "design" not in html_content.lower() and len(html_content) < 5000:
                enhanced_html = designer.create_modern_interface(plan['project_type'], idea)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_html)
        
        # 7. Debugger et Tester
        debugger.run_full_debug(project_path)
        tester.run_tests(project_path)
        
        # 8. Memory sauvegarde
        memory.add_project(project_id, idea)
        
        # 9. Lire les fichiers
        files = {}
        for filename in os.listdir(project_path):
            filepath = os.path.join(project_path, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        files[filename] = f.read()
                except:
                    files[filename] = "[Binaire]"
        
        file_count = len([f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))])
        
        return jsonify({
            "success": True,
            "project_id": project_id,
            "project_idea": idea,
            "files": files,
            "steps": {
                "vision": f"Plan créé - Type: {plan['project_type']}, Complexité: {plan['complexity']}/5",
                "designer": f"Thème {designer.get_best_style(plan['project_type'])['name']} appliqué",
                "artisan": f"{file_count} fichiers générés",
                "sentinel": "Analyse de sécurité effectuée",
                "judge": f"Score qualité: {tester.quality_score}/100",
                "memory": "Projet sauvegardé"
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects', methods=['GET'])
def get_projects():
    return jsonify({"projects": memory.get_projects_list()})

@app.route('/api/continue', methods=['POST'])
def continue_project():
    data = request.get_json()
    project_id = data.get('project_id')
    project_path = os.path.join(PROJECTS_DIR, project_id)
    
    if not os.path.exists(project_path):
        return jsonify({"error": "Projet non trouvé"}), 404
    
    idea = ""
    plan_path = os.path.join(project_path, "plan.json")
    if os.path.exists(plan_path):
        with open(plan_path, 'r') as f:
            plan = json.load(f)
            idea = plan.get('idea', '')
    
    return jsonify({
        "success": True,
        "message": f"Projet {project_id} chargé",
        "project": {"id": project_id, "idea": idea}
    })

@app.route('/api/templates', methods=['GET'])
def get_templates():
    templates = [
        {"id": "ecommerce", "name": "E-commerce", "description": "Boutique en ligne"},
        {"id": "comptabilite", "name": "Comptabilité", "description": "Site de comptabilité avec 3 pages"},
        {"id": "portfolio", "name": "Portfolio", "description": "Portfolio photographe"},
        {"id": "blog", "name": "Blog", "description": "Blog personnel"},
        {"id": "todo", "name": "Todo List", "description": "Gestion de tâches"}
    ]
    return jsonify({"templates": templates})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    creation_keywords = ["crée", "creer", "génère", "genere", "fais", "fabrique", "site", "app"]
    if any(kw in message for kw in creation_keywords) and len(message) > 5:
        idea = message
        for kw in creation_keywords:
            idea = idea.replace(kw, "")
        idea = idea.strip()
        if idea and len(idea) > 3:
            return jsonify({
                "type": "confirmation",
                "response": f"🔐 Créer : '{idea}' ? (oui/non)",
                "idea": idea
            })
    
    if "projet" in message and ("liste" in message or "mémoire" in message):
        projects = memory.get_projects_list()
        if projects:
            response = "🧠 **Tes projets :**\n\n"
            for p in projects[-5:]:
                response += f"• {p['idea'][:50]}... (ID: {p['id']})\n"
            response += "\n💡 Dis /continue [ID] pour reprendre"
            return jsonify({"type": "message", "response": response})
    
    if "apprend" in message or "tendance" in message:
        stats = planner.get_statistics()
        response = f"🌐 **Ce que j'ai appris :**\n\n"
        response += f"📊 {stats['total_analyses']} projets analysés\n"
        response += f"🎯 Types populaires : {', '.join(list(stats['project_types'].keys())[:3])}\n"
        return jsonify({"type": "message", "response": response})
    
    return jsonify({
        "type": "message",
        "response": f"👋 {message}\n\n💡 Pour créer une app, dis 'crée [idée]'"
    })

@app.route('/api/download/<project_id>', methods=['GET'])
def download_project(project_id):
    project_path = os.path.join(PROJECTS_DIR, project_id)
    if not os.path.exists(project_path):
        return jsonify({"error": "Projet non trouvé"}), 404
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_path):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, project_path)
                zf.write(filepath, arcname)
    
    memory_file.seek(0)
    return send_file(memory_file, download_name=f"orvia_project_{project_id}.zip", as_attachment=True)

@app.route('/api/preview-live/<project_id>', methods=['GET'])
def preview_live(project_id):
    project_path = os.path.join(PROJECTS_DIR, project_id)
    html_path = os.path.join(project_path, "index.html")
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    return jsonify({"error": "Fichier non trouvé"}), 404

@app.route('/api/learn/trends', methods=['GET'])
def learn_trends():
    stats = planner.get_statistics()
    return jsonify({
        "trends": {
            "design": ["Glassmorphism", "Neumorphism", "Dark mode", "Minimalist"],
            "frameworks": ["Flask", "FastAPI"],
            "databases": ["SQLite", "PostgreSQL"]
        },
        "stats": {
            "total_learned": stats['total_analyses'],
            "project_types": stats['project_types']
        }
    })

@app.route('/api/learn', methods=['POST'])
def learn():
    return jsonify({
        "success": True,
        "results": {
            "analysis": {"design": "Moderne", "technologies": ["HTML5", "CSS3"]},
            "learning": {"learned": 1, "words": ["apprentissage"]}
        }
    })

@app.route('/api/learn/recommend', methods=['POST'])
def learn_recommend():
    return jsonify({
        "success": True,
        "recommendations": {
            "design": "Glassmorphism",
            "colors": ["#667eea", "#764ba2"],
            "features": ["Authentification", "Base de données"]
        }
    })

# ========== LANCEMENT ==========

if __name__ == '__main__':
    # Utiliser le port fourni par Railway (8080 par défaut)
    port = int(os.environ.get('PORT', 8080))
    print("\n" + "="*60)
    print("🚀 ORVIA API - Tous les agents sont prêts !")
    print("="*60)
    print(f"📡 Serveur sur http://0.0.0.0:{port}")
    print("🤖 Agents: VISION, ARTISAN, SENTINEL, JUDGE, DESIGNER, MÉMOIRE")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=True)
