"""
ORVIA - API principale
Expose les agents via des endpoints REST
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import uuid
import shutil
import zipfile
from io import BytesIO
from datetime import datetime

# Import des agents
from agents.planner import Planner
from agents.coder import Coder
from agents.designer import Designer
from agents.debugger import Debugger
from agents.tester import Tester
from agents.memory import Memory

app = Flask(__name__)
CORS(app)  # Permet au frontend de communiquer

# Initialisation des agents
planner = Planner()
coder = Coder()
designer = Designer()
debugger = Debugger()
tester = Tester()
memory = Memory()

# Dossier pour les projets générés
PROJECTS_DIR = "generated_projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Dossier temporaire pour generated_project
TEMP_DIR = "generated_project"

# ========== ROUTES PRINCIPALES ==========

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
    """Génère une application à partir d'une idée"""
    data = request.get_json()
    idea = data.get('idea', '')
    
    if not idea:
        return jsonify({"error": "Aucune idée fournie"}), 400
    
    print(f"🚀 Génération pour : {idea}")
    
    try:
        # Étape 1: Planner crée le plan
        plan = planner.create_plan(idea)
        
        # Étape 2: Coder génère le code
        success, message = coder.generate_code(None, plan)
        
        if not success:
            return jsonify({"error": message}), 500
        
        # Étape 3: Créer le dossier du projet
        project_id = plan['id']
        project_path = os.path.join(PROJECTS_DIR, project_id)
        os.makedirs(project_path, exist_ok=True)
        
        # Déplacer les fichiers générés depuis TEMP_DIR
        if os.path.exists(TEMP_DIR):
            for file in os.listdir(TEMP_DIR):
                src = os.path.join(TEMP_DIR, file)
                dst = os.path.join(project_path, file)
                if os.path.isfile(src):
                    shutil.move(src, dst)
        
        # Sauvegarder le plan
        with open(os.path.join(project_path, "plan.json"), 'w') as f:
            json.dump(plan, f, indent=2)
        
        # Étape 4: Designer améliore l'interface
        html_path = os.path.join(project_path, "index.html")
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Améliorer avec le designer si besoin
            if "design" not in html_content.lower() and len(html_content) < 5000:
                enhanced_html = designer.create_modern_interface(plan['project_type'], idea)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_html)
        
        # Étape 5: Debugger vérifie
        debugger.run_full_debug(project_path)
        
        # Étape 6: Tester valide
        tester.run_tests(project_path)
        
        # Étape 7: Memory sauvegarde
        memory.add_project(project_id, idea)
        
        # Lire les fichiers générés pour les renvoyer
        files = {}
        for filename in os.listdir(project_path):
            filepath = os.path.join(project_path, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        files[filename] = f.read()
                except:
                    files[filename] = "[Binaire]"
        
        # Compter les fichiers
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
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Liste tous les projets"""
    projects = memory.get_projects_list()
    return jsonify({"projects": projects})

@app.route('/api/continue', methods=['POST'])
def continue_project():
    """Continue un projet existant"""
    data = request.get_json()
    project_id = data.get('project_id')
    
    project_path = os.path.join(PROJECTS_DIR, project_id)
    
    if not os.path.exists(project_path):
        return jsonify({"error": "Projet non trouvé"}), 404
    
    # Lire l'idée depuis le plan
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
    """Retourne les templates disponibles"""
    templates = [
        {"id": "ecommerce", "name": "E-commerce", "description": "Boutique en ligne avec panier et paiement"},
        {"id": "comptabilite", "name": "Comptabilité", "description": "Site de comptabilité avec graphiques et 3 pages"},
        {"id": "portfolio", "name": "Portfolio", "description": "Portfolio pour photographe/artiste avec galerie"},
        {"id": "blog", "name": "Blog", "description": "Blog personnel avec articles et commentaires"},
        {"id": "todo", "name": "Todo List", "description": "Gestion de tâches avec priorités et catégories"}
    ]
    return jsonify({"templates": templates})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Dialogue avec ORVIA"""
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Détection d'intention de création
    creation_keywords = ["crée", "creer", "génère", "genere", "fais", "fabrique", "site", "app"]
    if any(kw in message for kw in creation_keywords) and len(message) > 5:
        # Extraire l'idée
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
    
    # Mots-clés pour mémoire
    if "projet" in message and ("liste" in message or "mémoire" in message or "montre" in message):
        projects = memory.get_projects_list()
        if projects:
            response = "🧠 **Tes projets :**\n\n"
            for p in projects[-5:]:
                response += f"• {p['idea'][:50]}... (ID: {p['id']})\n"
            response += "\n💡 Dis /continue [ID] pour reprendre"
            return jsonify({"type": "message", "response": response})
        else:
            return jsonify({"type": "message", "response": "📭 Tu n'as pas encore de projets. Dis 'crée un site...' pour commencer !"})
    
    # Apprentissage
    if "apprend" in message or "tendance" in message:
        stats = planner.get_statistics()
        response = f"🌐 **Ce que j'ai appris :**\n\n"
        response += f"📊 {stats['total_analyses']} projets analysés\n"
        response += f"🎯 Types populaires : {', '.join(list(stats['project_types'].keys())[:3])}\n"
        if stats['common_features']:
            response += f"✨ Fonctionnalités courantes : {', '.join([f[0] for f in stats['common_features'][:3]])}"
        return jsonify({"type": "message", "response": response})
    
    # Salutations
    if any(g in message for g in ["bonjour", "salut", "hello", "coucou"]):
        return jsonify({
            "type": "message",
            "response": "👋 Bonjour ! Je suis ORVIA, ton assistant IA. Dis-moi ce que tu veux créer !"
        })
    
    # Réponse par défaut
    return jsonify({
        "type": "message",
        "response": f"👋 {message}\n\n💡 Pour créer une app, dis 'crée [idée]' ou '/generate [idée]'"
    })

@app.route('/api/download/<project_id>', methods=['GET'])
def download_project(project_id):
    """Télécharge le projet au format ZIP"""
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
    return memory_file.getvalue(), 200, {
        'Content-Type': 'application/zip',
        'Content-Disposition': f'attachment; filename=orvia_project_{project_id}.zip'
    }

@app.route('/api/preview-live/<project_id>', methods=['GET'])
def preview_live(project_id):
    """Redirige vers le fichier index.html du projet"""
    project_path = os.path.join(PROJECTS_DIR, project_id)
    html_path = os.path.join(project_path, "index.html")
    
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    
    return jsonify({"error": "Fichier non trouvé"}), 404

@app.route('/api/expo-preview/<project_id>', methods=['GET'])
def expo_preview(project_id):
    """Aperçu Expo (simulation)"""
    return jsonify({
        "message": "Preview Expo bientôt disponible",
        "project_id": project_id,
        "expo_link": f"https://expo.io/@orvia/project-{project_id}"
    })

@app.route('/api/learn/trends', methods=['GET'])
def learn_trends():
    """Retourne les tendances apprises"""
    stats = planner.get_statistics()
    return jsonify({
        "trends": {
            "design": ["Glassmorphism", "Neumorphism", "Dark mode", "Minimalist", "Brutalist", "Gradient", "Neon"],
            "frameworks": ["Flask", "FastAPI", "Django"],
            "databases": ["SQLite", "PostgreSQL", "MongoDB"]
        },
        "stats": {
            "total_learned": stats['total_analyses'],
            "project_types": stats['project_types']
        }
    })

@app.route('/api/learn', methods=['POST'])
def learn():
    """Apprentissage à partir d'une URL ou texte"""
    data = request.get_json()
    
    if data.get('url'):
        return jsonify({
            "success": True,
            "results": {
                "analysis": {
                    "url": data['url'],
                    "design": "Moderne",
                    "technologies": ["HTML5", "CSS3", "JavaScript"],
                    "performance": "Bonne"
                }
            }
        })
    
    if data.get('text'):
        return jsonify({
            "success": True,
            "results": {
                "learning": {
                    "learned": 1,
                    "words": data['text'][:50].split()[:5]
                }
            }
        })
    
    return jsonify({"error": "Aucune donnée fournie"}), 400

@app.route('/api/learn/recommend', methods=['POST'])
def learn_recommend():
    """Recommandations basées sur l'apprentissage"""
    data = request.get_json()
    project_type = data.get('project_type', 'generic')
    
    recommendations = {
        "design": "Glassmorphism avec fond dégradé",
        "colors": ["#667eea", "#764ba2", "#f093fb"],
        "features": ["Authentification", "Base de données", "Interface responsive"]
    }
    
    return jsonify({
        "success": True,
        "recommendations": recommendations
    })

# ========== LANCEMENT ==========

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print("\n" + "="*60)
    print("🚀 ORVIA API - Tous les agents sont prêts !")
    print("="*60)
    print(f"📡 Serveur sur http://localhost:{port}")
    print(f"🤖 Agents: VISION, ARTISAN, SENTINEL, JUDGE, DESIGNER, MÉMOIRE")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=True)
