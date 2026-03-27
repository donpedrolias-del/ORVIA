"""
ORVIA - IA INTELLIGENTE
Comprend les questions et les demandes de création
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import json
import shutil
import subprocess
import threading
import re
from datetime import datetime
import sys
import pickle
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ========== DEEPSEEK API ==========
DEEPSEEK_API_KEY = "sk-226b39f55f5e4d5eb13fda8772aa4c57"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# ========== GESTIONNAIRE D'APPS ==========
running_apps = {}

def start_app_background(project_id, project_path):
    backend_path = os.path.join(project_path, "backend.py")
    if not os.path.exists(backend_path):
        return False
    def run_server():
        try:
            os.chdir(project_path)
            process = subprocess.Popen(["python3", "backend.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            running_apps[project_id] = process
            time.sleep(2)
        except:
            pass
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()
    return True

# ========== MÉMOIRE ==========
class Memory:
    def __init__(self):
        self.memory_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orvia_memory.pkl")
        self.projects = []
        self.load_memory()
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'rb') as f:
                    data = pickle.load(f)
                    self.projects = data.get("projects", [])
                print(f"🧠 Mémoire: {len(self.projects)} projets")
            except:
                pass
    def save_memory(self):
        with open(self.memory_file, 'wb') as f:
            pickle.dump({"projects": self.projects}, f)
    def add_project(self, project_id, idea):
        self.projects.append({"id": project_id, "idea": idea, "created_at": datetime.now().isoformat()})
        self.save_memory()
    def get_projects_list(self):
        return self.projects

memory_agent = Memory()

# ========== AGENT LEARNER ==========
class Learner:
    def __init__(self):
        self.knowledge_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge.json")
        self.knowledge = self.load_knowledge()
    def load_knowledge(self):
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"trends": {"design": ["Glassmorphism", "Neumorphism", "Dark mode", "Minimalist", "Brutalist"]}, "learned": [], "last_update": datetime.now().isoformat()}
    def save_knowledge(self):
        self.knowledge["last_update"] = datetime.now().isoformat()
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
    def search_trends(self, category="design"):
        return self.knowledge["trends"].get(category, ["Glassmorphism", "Neumorphism", "Dark mode"])
    def get_recommendations(self, project_type):
        recos = {
            "ecommerce": {"design": "Moderne avec grands visuels", "colors": ["#2c3e50", "#3498db", "#e74c3c"]},
            "portfolio": {"design": "Minimaliste avec animations", "colors": ["#000000", "#ffffff", "#9b59b6"]},
            "comptabilite": {"design": "Professionnel épuré", "colors": ["#1e3a8a", "#10b981", "#f8fafc"]}
        }
        for key in recos:
            if key in project_type.lower():
                return recos[key]
        return recos["portfolio"]
    def learn_from_text(self, text):
        keywords = re.findall(r'\b[A-Za-z]{4,}\b', text)
        new_words = [k for k in keywords if k not in str(self.knowledge)]
        if new_words:
            self.knowledge["learned"].append({"date": datetime.now().isoformat(), "content": text[:200], "keywords": new_words[:5]})
            self.save_knowledge()
            return {"learned": len(new_words), "words": new_words[:3]}
        return {"learned": 0}
    def get_learning_stats(self):
        return {"total_learned": len(self.knowledge["learned"]), "last_update": self.knowledge["last_update"]}

learner_agent = Learner()

app = Flask(__name__)
CORS(app)

GENERATED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_projects")
os.makedirs(GENERATED_DIR, exist_ok=True)

# ========== VARIABLES DE CONFIRMATION ==========
waiting_for_confirmation = False
pending_idea = None

def get_orvia_response(message, projects_count):
    system_prompt = f"""Tu es ORVIA, un assistant IA chaleureux et intelligent.
Tu as une équipe de 6 agents: 🔮 VISION, ✨ ARTISAN, 🛡️ SENTINEL, ⚖️ JUDGE, 🎨 DESIGNER, 🧠 MÉMOIRE.
Tu as déjà créé {projects_count} applications.

RÈGLES:
- Tu réponds en français, avec des emojis
- Tu es chaleureux et enthousiaste
- Si l'utilisateur pose une question, tu réponds à la question
- Si l'utilisateur demande de créer quelque chose, tu dis que tu es prêt et tu demandes confirmation
- Tu ne crées JAMAIS sans confirmation explicite

Tu réponds au format JSON avec un champ "response"."""
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
            "temperature": 0.8,
            "max_tokens": 300
        }
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    if "response" in parsed:
                        return parsed["response"]
                except:
                    pass
            return content
    except:
        pass
    return None

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    global waiting_for_confirmation, pending_idea
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Dis-moi quelque chose !"}), 400
        
        print(f"\n📨 Message: {message}")
        msg_lower = message.lower()
        
        # ========== 1. GESTION DE LA CONFIRMATION ==========
        if waiting_for_confirmation and msg_lower in ["oui", "yes", "ok", "o", "créé", "cree", "oui crée", "oui cree"]:
            waiting_for_confirmation = False
            idea = pending_idea
            pending_idea = None
            return jsonify({
                "type": "chat",
                "response": "🚀 Lancement de la création !",
                "should_create": True,
                "idea": idea
            })
        
        if waiting_for_confirmation and msg_lower in ["non", "no", "n", "annule", "annuler"]:
            waiting_for_confirmation = False
            pending_idea = None
            return jsonify({"type": "chat", "response": "🔒 Annulé."})
        
        # ========== 2. COMMANDES SPÉCIALES ==========
        
        if msg_lower.startswith('/template'):
            template_name = msg_lower.replace('/template', '').strip()
            templates = {
                "ecommerce": "site e-commerce complet avec catalogue produits, panier, catégories et authentification JWT",
                "comptabilite": "site de comptabilité avec accueil, informations, développement, graphiques de dépenses",
                "portfolio": "portfolio photographe avec galerie d'images, formulaire de contact",
                "blog": "blog personnel avec articles, commentaires, catégories",
                "todo": "application de gestion de tâches avec catégories, priorités, recherche"
            }
            if template_name in templates:
                idea = templates[template_name]
                waiting_for_confirmation = True
                pending_idea = idea
                return jsonify({
                    "type": "confirmation",
                    "response": f"🎨 Template '{template_name}' chargé !\n\n{idea}\n\n🔐 Créer cette application ? (oui/non)",
                    "idea": idea
                })
            else:
                return jsonify({"type": "chat", "response": "📁 Templates: ecommerce, comptabilite, portfolio, blog, todo"})
        
        if msg_lower.startswith('/generate'):
            idea = msg_lower.replace('/generate', '').strip()
            if idea:
                waiting_for_confirmation = True
                pending_idea = idea
                return jsonify({
                    "type": "confirmation",
                    "response": f"🔐 Créer : '{idea}' ? (oui/non)",
                    "idea": idea
                })
        
        if msg_lower.startswith('/learn'):
            if 'trends' in msg_lower:
                trends = learner_agent.search_trends('design')
                return jsonify({"type": "chat", "response": f"📊 Tendances design: {', '.join(trends)}"})
            elif 'recommend' in msg_lower:
                recos = learner_agent.get_recommendations('ecommerce')
                return jsonify({"type": "chat", "response": f"💡 Recommandations: {recos['design']} - Couleurs: {', '.join(recos['colors'])}"})
            else:
                return jsonify({"type": "chat", "response": "🌐 Utilise /learn trends ou /learn recommend"})
        
        # ========== 3. DÉTECTION D'UNE DEMANDE DE CRÉATION ==========
        creation_keywords = ["crée", "créer", "fais-moi", "je veux", "génère", "construis", "fais", "site", "application", "app"]
        is_question = "?" in message or any(word in msg_lower for word in ["pourquoi", "comment", "quel", "quelle", "combien", "où", "quand", "qui", "est-ce"])
        
        # Si c'est une demande de création ET que ce n'est pas une question
        if not is_question and any(word in msg_lower for word in creation_keywords):
            # Extraire l'idée
            idea = message
            for word in ["crée", "créer", "fais-moi", "je veux", "génère", "construis", "une", "un", "application", "site", "fais", "moi"]:
                if idea.lower().startswith(word):
                    idea = idea[len(word):].strip()
            if not idea or len(idea) < 5:
                idea = message
            
            waiting_for_confirmation = True
            pending_idea = idea
            
            return jsonify({
                "type": "confirmation",
                "response": f"🔐 Créer : '{idea}' ? (oui/non)",
                "idea": idea
            })
        
        # ========== 4. CONVERSATION NORMALE ==========
        projects_count = len(memory_agent.get_projects_list())
        ai_response = get_orvia_response(message, projects_count)
        
        if ai_response:
            return jsonify({"type": "chat", "response": ai_response})
        
        # Fallback
        if any(word in msg_lower for word in ["bonjour", "salut"]):
            return jsonify({"type": "chat", "response": "👋 Bonjour ! Je suis ORVIA, ton assistant IA. Comment puis-je t'aider ?"})
        
        if any(word in msg_lower for word in ["ça va", "vas bien"]):
            return jsonify({"type": "chat", "response": "👍 Je vais très bien, merci ! Et toi ?"})
        
        if any(word in msg_lower for word in ["merci"]):
            return jsonify({"type": "chat", "response": "🌟 Avec plaisir !"})
        
        return jsonify({"type": "chat", "response": "💡 Je suis ORVIA. Parle-moi normalement, je te comprends ! Pour créer une application, dis-moi 'crée un site de comptabilité'."})
        
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        idea = data.get('idea', '')
        if not idea:
            return jsonify({"error": "Donne-moi une idée !"}), 400
        
        project_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_path = os.path.join(GENERATED_DIR, project_id)
        os.makedirs(project_path, exist_ok=True)
        
        backend = '''"""
Application générée par ORVIA
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

data = []
counter = 1

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify({"items": data, "total": len(data)})

@app.route('/api/items', methods=['POST'])
def create_item():
    global counter
    item_data = request.get_json()
    item = {"id": counter, "data": item_data, "created_at": datetime.now().isoformat()}
    counter += 1
    data.append(item)
    return jsonify(item), 201

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global data
    new_data = []
    for item in data:
        if item['id'] != item_id:
            new_data.append(item)
    data = new_data
    return jsonify({"message": "Supprimé"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5008))
    app.run(host='0.0.0.0', port=port, debug=True)'''
        
        with open(os.path.join(project_path, "backend.py"), 'w') as f:
            f.write(backend)
        
        with open(os.path.join(project_path, "requirements.txt"), 'w') as f:
            f.write("Flask==2.3.2\nflask-cors==4.0.0\n")
        
        html = f'''<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>ORVIA - {idea[:40]}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 20px; }}
.container {{ max-width: 800px; margin: 0 auto; }}
.card {{ background: white; border-radius: 24px; padding: 30px; margin-bottom: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
h1 {{ color: #667eea; margin-bottom: 20px; }}
input {{ width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 12px; margin: 10px 0; }}
button {{ background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 12px; cursor: pointer; width: 100%; }}
.item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 12px; display: flex; justify-content: space-between; }}
.delete-btn {{ background: #dc3545; padding: 5px 10px; width: auto; }}
.stats {{ display: flex; gap: 20px; margin: 20px 0; }}
.stat-card {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 15px; border-radius: 15px; flex: 1; text-align: center; }}
.stat-card h3 {{ font-size: 2rem; }}
</style>
</head>
<body>
<div class="container">
<div class="card"><h1>✨ {idea[:60]}</h1><p>Généré par ORVIA</p></div>
<div class="card">
<div class="stats"><div class="stat-card"><h3 id="total">0</h3><p>Éléments</p></div><div class="stat-card"><h3 id="apiStatus">...</h3><p>API</p></div></div>
<input type="text" id="inputData" placeholder="Ajouter..."><button onclick="addItem()">Ajouter</button>
<div id="itemsList"></div>
</div>
</div>
<script>
const API_URL='http://127.0.0.1:5002';let items=[];
async function checkAPI(){{try{{const r=await fetch(API_URL+'/api/status');if(r.ok)document.getElementById('apiStatus').textContent='✅ Online';}}catch(e){{document.getElementById('apiStatus').textContent='❌ Offline';}}}}
async function loadItems(){{try{{const r=await fetch(API_URL+'/api/items');const d=await r.json();items=d.items;document.getElementById('total').textContent=items.length;
const c=document.getElementById('itemsList');if(items.length===0)c.innerHTML='<p style="text-align:center;">📭 Aucun élément</p>';
else{{let h='';for(let i=0;i<items.length;i++){{const it=items[i];h+='<div class="item"><div><strong>#'+it.id+'</strong> '+(it.data?(it.data.value||it.data):'')+'<br><small>'+new Date(it.created_at).toLocaleString()+'</small></div><button class="delete-btn" onclick="deleteItem('+it.id+')">🗑️</button></div>';}}c.innerHTML=h;}}}}catch(e){{console.error(e);}}}}
async function addItem(){{const i=document.getElementById('inputData'),v=i.value.trim();if(!v)return;
try{{const r=await fetch(API_URL+'/api/items',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{value:v}})}});if(r.ok){{i.value='';loadItems();}}}}
catch(e){{const ni={{id:Date.now(),data:{{value:v}},created_at:new Date().toISOString()}};items.push(ni);document.getElementById('total').textContent=items.length;
let h='';for(let i=0;i<items.length;i++){{const it=items[i];h+='<div class="item"><div><strong>#'+it.id+'</strong> '+(it.data?(it.data.value||it.data):'')+'<br><small>'+new Date(it.created_at).toLocaleString()+'</small></div><button class="delete-btn" onclick="deleteItem('+it.id+')">🗑️</button></div>';}}document.getElementById('itemsList').innerHTML=h;i.value='';}}}}
async function deleteItem(id){{try{{await fetch(API_URL+'/api/items/'+id,{{method:'DELETE'}});loadItems();}}catch(e){{items=items.filter(i=>i.id!==id);document.getElementById('total').textContent=items.length;
let h='';for(let i=0;i<items.length;i++){{const it=items[i];h+='<div class="item"><div><strong>#'+it.id+'</strong> '+(it.data?(it.data.value||it.data):'')+'<br><small>'+new Date(it.created_at).toLocaleString()+'</small></div><button class="delete-btn" onclick="deleteItem('+it.id+')">🗑️</button></div>';}}document.getElementById('itemsList').innerHTML=h;}}}}
checkAPI();loadItems();setInterval(()=>{{checkAPI();loadItems();}},3000);
</script>
</body>
</html>'''
        
        with open(os.path.join(project_path, "index.html"), 'w') as f:
            f.write(html)
        
        info = {"id": project_id, "idea": idea, "created_at": datetime.now().isoformat(), "files": ["backend.py", "index.html", "requirements.txt"]}
        with open(os.path.join(project_path, "info.json"), 'w') as f:
            json.dump(info, f, indent=2)
        
        memory_agent.add_project(project_id, idea)
        
        steps = [
            {"agent": "ORVIA", "action": "Réception", "detail": idea, "icon": "👑"},
            {"agent": "VISION", "action": "Analyse", "detail": "Planification", "icon": "🔮"},
            {"agent": "ARTISAN", "action": "Génération", "detail": "Code créé", "icon": "✨"},
            {"agent": "SENTINEL", "action": "Scan", "detail": "Sécurité OK", "icon": "🛡️"},
            {"agent": "JUDGE", "action": "Validation", "detail": "Tests OK", "icon": "⚖️"},
            {"agent": "DESIGNER", "action": "Design", "detail": "Interface", "icon": "🎨"},
            {"agent": "ORVIA", "action": "Mission accomplie", "detail": "Projet prêt", "icon": "🏆"}
        ]
        
        start_app_background(project_id, project_path)
        
        return jsonify({
            "success": True,
            "project_id": project_id,
            "idea": idea,
            "files": ["backend.py", "index.html", "requirements.txt"],
            "steps": steps,
            "message": "Mission accomplie !"
        }), 201
        
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<project_id>', methods=['GET'])
def download_project(project_id):
    project_path = os.path.join(GENERATED_DIR, project_id)
    if not os.path.exists(project_path):
        return jsonify({"error": "Projet non trouvé"}), 404
    zip_path = f"/tmp/{project_id}.zip"
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', project_path)
    return send_file(zip_path, as_attachment=True, download_name=f"{project_id}.zip")

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"status": "online", "team": "ORVIA", "projects": len(memory_agent.projects)})

@app.route('/api/preview-live/<project_id>', methods=['GET'])
def preview_live(project_id):
    project_path = os.path.join(GENERATED_DIR, project_id)
    if not os.path.exists(project_path):
        return jsonify({"error": "Projet non trouvé"}), 404
    return send_file(os.path.join(project_path, "index.html"))

@app.route('/api/preview-content/<project_id>', methods=['GET'])
def preview_content(project_id):
    project_path = os.path.join(GENERATED_DIR, project_id)
    index_path = os.path.join(project_path, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return f.read()
    return '<html><body><h2>🚀 Chargement...</h2></body></html>'

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = []
    gen_dir = GENERATED_DIR
    if os.path.exists(gen_dir):
        for pid in os.listdir(gen_dir):
            info_path = os.path.join(gen_dir, pid, "info.json")
            if os.path.exists(info_path):
                try:
                    with open(info_path, 'r') as f:
                        projects.append(json.load(f))
                except:
                    pass
    return jsonify({"projects": sorted(projects, key=lambda x: x.get('created_at', ''), reverse=True)})

@app.route('/api/project/<project_id>', methods=['GET'])
def get_project(project_id):
    project_path = os.path.join(GENERATED_DIR, project_id)
    info_path = os.path.join(project_path, "info.json")
    if os.path.exists(info_path):
        with open(info_path, 'r') as f:
            project = json.load(f)
        return jsonify({"success": True, "project": project})
    return jsonify({"success": False, "error": "Projet non trouvé"}), 404

@app.route('/api/continue', methods=['POST'])
def continue_project():
    try:
        data = request.get_json()
        project_id = data.get('project_id', '')
        if not project_id:
            return jsonify({"error": "ID du projet requis"}), 400
        project_path = os.path.join(GENERATED_DIR, project_id)
        info_path = os.path.join(project_path, "info.json")
        if not os.path.exists(info_path):
            return jsonify({"error": "Projet non trouvé"}), 404
        with open(info_path, 'r') as f:
            project = json.load(f)
        start_app_background(project_id, project_path)
        return jsonify({"success": True, "project": project, "message": f"Projet '{project['idea'][:50]}' chargé !"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    templates = [
        {"id": "ecommerce", "name": "🛒 E-commerce", "description": "Boutique en ligne", "idea": "site e-commerce complet"},
        {"id": "comptabilite", "name": "📊 Comptabilité", "description": "Site de comptabilité", "idea": "site de comptabilité"},
        {"id": "portfolio", "name": "🎨 Portfolio", "description": "Portfolio artistique", "idea": "portfolio photographe"},
        {"id": "blog", "name": "📝 Blog", "description": "Blog personnel", "idea": "blog personnel"},
        {"id": "todo", "name": "📋 Todo List", "description": "Gestion de tâches", "idea": "application de gestion de tâches"}
    ]
    return jsonify({"templates": templates})

@app.route('/api/learn', methods=['POST'])
def learn():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if text:
            learning = learner_agent.learn_from_text(text)
            return jsonify({"success": True, "message": "ORVIA a appris !", "learning": learning})
        return jsonify({"error": "Rien à apprendre"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/learn/trends', methods=['GET'])
def get_trends():
    trends = learner_agent.search_trends('design')
    return jsonify({"trends": trends, "stats": learner_agent.get_learning_stats()})

@app.route('/api/learn/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        project_type = data.get('project_type', 'generic')
        recos = learner_agent.get_recommendations(project_type)
        return jsonify({"success": True, "recommendations": recos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5008))
    print("\n" + "="*60)
    print("🏆 ORVIA - IA INTELLIGENTE")
    print("="*60)
    print(f"🌐 http://localhost:{port}")
    print("🧠 ORVIA comprend les questions et les demandes de création")
    print("💬 Pose une question → il répond")
    print("🚀 Dis 'crée un site' → il demande confirmation")
    print("✅ Dis 'oui' → il crée l'application")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True)
