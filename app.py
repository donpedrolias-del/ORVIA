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
import random

# Import des agents
try:
    from agents.planner import Planner
    from agents.coder import Coder
    from agents.designer import Designer
    from agents.debugger import Debugger
    from agents.tester import Tester
    from agents.memory import Memory
    from agents.dictionary import Dictionary
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
dictionary = Dictionary()

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
        "agents": ["vision", "artisan", "sentinel", "judge", "designer", "memoire", "dictionary"]
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
        # Utiliser le dictionnaire pour améliorer la détection
        project_type = dictionary.detect_project_type(idea)
        
        # 1. Planner crée le plan
        plan = planner.create_plan(idea)
        plan['project_type'] = project_type
        
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
                enhanced_html = designer.create_modern_interface(project_type, idea)
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
                "vision": f"Plan créé - Type: {project_type}, Complexité: {plan['complexity']}/5",
                "designer": f"Thème {designer.get_best_style(project_type)['name']} appliqué",
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

# ========== CHAT AMÉLIORÉ ==========

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # ========== COMMANDES SPÉCIALES ==========
    
    # Commande pour voir le dictionnaire
    if message == "montre ton dictionnaire" or message == "dictionnaire" or message == "vocabulaire":
        stats = dictionary.get_stats()
        response = f"📖 **Mon dictionnaire :**\n\n"
        response += f"• {stats['total_words']} mots appris\n"
        response += f"• {stats['total_expressions']} expressions\n"
        response += f"• {stats['total_categories']} catégories\n\n"
        response += f"**Catégories :** {', '.join(stats['categories_list'])}\n\n"
        response += f"**Mots :** {', '.join(dictionary.get_all_words()[:10])}\n\n"
        response += f"💡 Pour m'apprendre un mot : `/learn mot [mot]`"
        return jsonify({"type": "message", "response": response})
    
    # Commande pour apprendre un mot
    if message.startswith("/learn mot"):
        parts = message.replace("/learn mot", "").strip().split()
        if parts:
            word = parts[0]
            meaning = " ".join(parts[1:]) if len(parts) > 1 else word
            success, msg = dictionary.learn_word(word, "general", meaning)
            return jsonify({"type": "message", "response": msg})
        else:
            return jsonify({"type": "message", "response": "📝 Utilisation : `/learn mot [mot] [signification]`"})
    
    # Commande pour apprendre une expression
    if message.startswith("/learn expression"):
        expr = message.replace("/learn expression", "").strip()
        if expr:
            success, msg = dictionary.learn_expression(expr, expr)
            return jsonify({"type": "message", "response": msg})
        else:
            return jsonify({"type": "message", "response": "📝 Utilisation : `/learn expression [phrase]`"})
    
    # Commande pour apprendre une catégorie
    if message.startswith("/learn categorie"):
        parts = message.replace("/learn categorie", "").strip().split()
        if len(parts) >= 2:
            category = parts[0]
            keywords = parts[1:]
            success, msg = dictionary.learn_category(category, keywords)
            return jsonify({"type": "message", "response": msg})
        else:
            return jsonify({"type": "message", "response": "📝 Utilisation : `/learn categorie [nom] [mot-clé1 mot-clé2 ...]`"})
    
    # ========== CONVERSATION NORMALE ==========
    
    # Salutations
    greetings = ["bonjour", "salut", "hello", "coucou", "hey", "yo"]
    if any(g in message for g in greetings):
        responses = [
            "👋 Bonjour ! Comment puis-je t'aider aujourd'hui ?",
            "🌟 Salut ! Je suis ORVIA, prêt à créer des applications pour toi !",
            "🎨 Coucou ! Tu veux créer une application ?"
        ]
        return jsonify({"type": "message", "response": random.choice(responses)})
    
    # Questions sur ORVIA
    if "qui es-tu" in message or "présente-toi" in message or "c'est quoi orvia" in message:
        return jsonify({
            "type": "message",
            "response": "🤖 **Je suis ORVIA** - L'intelligence qui crée des applications !\n\n"
                        "J'ai 7 agents à mon service :\n"
                        "• 🔮 VISION - Planifie ton projet\n"
                        "• ✨ ARTISAN - Écrit le code\n"
                        "• 🛡️ SENTINEL - Vérifie la sécurité\n"
                        "• ⚖️ JUDGE - Teste la qualité\n"
                        "• 🎨 DESIGNER - Crée l'interface\n"
                        "• 🧠 MÉMOIRE - Se souvient de tout\n"
                        "• 📚 DICTIONNAIRE - Apprend de nouveaux mots\n\n"
                        "💡 Dis-moi ce que tu veux créer !"
        })
    
    # Questions sur les fonctionnalités
    if "fonctionnalité" in message or "sais faire" in message or "compétences" in message:
        return jsonify({
            "type": "message",
            "response": "✨ **Mes fonctionnalités :**\n\n"
                        "• 🚀 Créer des applications web (sites, API, blogs, e-commerce...)\n"
                        "• 🧠 Apprendre de nouveaux mots et expressions\n"
                        "• 📁 Sauvegarder tous tes projets\n"
                        "• 🎨 Appliquer des designs modernes (Glassmorphism, Dark mode...)\n"
                        "• 🔒 Sécuriser avec authentification JWT\n"
                        "• 📱 Générer des applications React Native (Expo)\n\n"
                        "💡 Essaie : 'crée un site portfolio'"
        })
    
    # Détection d'intention de création
    creation_keywords = ["crée", "creer", "génère", "genere", "fais", "fabrique", "site", "app",
                         "application", "créer", "générer", "veux", "aimerais", "faire", "construire"]
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
    
    # Demande de templates
    if "template" in message or "modèle" in message:
        return jsonify({
            "type": "message",
            "response": "🎨 **Templates disponibles :**\n\n"
                        "• ecommerce - Boutique en ligne\n"
                        "• portfolio - Portfolio artistique\n"
                        "• blog - Blog personnel\n"
                        "• todo - Liste de tâches\n"
                        "• comptabilite - Site comptable\n\n"
                        "👉 Tape /template [nom] pour l'utiliser"
        })
    
    # Réponse par défaut pour les conversations normales
    default_responses = [
        f"👋 {message}\n\n💡 Pour créer une application, dis 'crée [idée]'",
        f"✨ Je t'écoute ! {message}\n\nDis-moi ce que tu veux créer !",
        f"😊 {message}\n\nVeux-tu que je crée une application pour toi ?",
        f"🎨 Intéressant ! {message}\n\nSi tu veux créer une app, dis-moi !"
    ]
    return jsonify({"type": "message", "response": random.choice(default_responses)})

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

@app.route('/api/expo-preview/<project_id>', methods=['GET'])
def expo_preview(project_id):
    return jsonify({
        "message": "Preview Expo bientôt disponible",
        "project_id": project_id
    })

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

# ========== ROUTES DU DICTIONNAIRE ==========

@app.route('/api/dictionary/learn', methods=['POST'])
def learn_word():
    data = request.get_json()
    word = data.get('word', '')
    category = data.get('category', 'general')
    meaning = data.get('meaning', '')
    
    if not word:
        return jsonify({"error": "Aucun mot fourni"}), 400
    
    success, message = dictionary.learn_word(word, category, meaning)
    return jsonify({
        "success": success,
        "message": message,
        "stats": dictionary.get_stats()
    })

@app.route('/api/dictionary/expression', methods=['POST'])
def learn_expression():
    data = request.get_json()
    expression = data.get('expression', '')
    meaning = data.get('meaning', '')
    
    if not expression:
        return jsonify({"error": "Aucune expression fournie"}), 400
    
    success, message = dictionary.learn_expression(expression, meaning)
    return jsonify({
        "success": success,
        "message": message,
        "stats": dictionary.get_stats()
    })

@app.route('/api/dictionary/category', methods=['POST'])
def learn_category():
    data = request.get_json()
    category = data.get('category', '')
    keywords = data.get('keywords', [])
    
    if not category:
        return jsonify({"error": "Aucune catégorie fournie"}), 400
    
    success, message = dictionary.learn_category(category, keywords)
    return jsonify({
        "success": success,
        "message": message,
        "stats": dictionary.get_stats()
    })

@app.route('/api/dictionary/stats', methods=['GET'])
def dictionary_stats():
    return jsonify(dictionary.get_stats())

@app.route('/api/dictionary/words', methods=['GET'])
def dictionary_words():
    return jsonify({
        "words": dictionary.get_all_words(),
        "total": len(dictionary.get_all_words())
    })

@app.route('/api/dictionary/understand', methods=['POST'])
def understand_text():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "Aucun texte fourni"}), 400
    
    result = dictionary.understand(text)
    result["detected_type"] = dictionary.detect_project_type(text)
    return jsonify(result)

# ========== LANCEMENT ==========

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("\n" + "="*60)
    print("🚀 ORVIA API - Tous les agents sont prêts !")
    print("="*60)
    print(f"📡 Serveur sur http://0.0.0.0:{port}")
    print("🤖 Agents: VISION, ARTISAN, SENTINEL, JUDGE, DESIGNER, MÉMOIRE, DICTIONNAIRE")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=True)
