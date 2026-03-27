"""
Planner Agent - VISION PRO
Analyse avancée, détection de patterns, apprentissage continu
"""

import uuid
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

class Planner:
    def __init__(self):
        self.memory_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory", "planner_memory.json")
        self.load_memory()
    
    def load_memory(self):
        """Charge la mémoire des patterns appris"""
        self.patterns = {
            "project_types": {},
            "feature_detection": {},
            "complexity_patterns": {},
            "successful_patterns": []
        }
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    loaded = json.load(f)
                    self.patterns.update(loaded)
                print("🧠 VISION: Mémoire chargée")
            except:
                pass
    
    def save_memory(self):
        """Sauvegarde les patterns appris"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def create_plan(self, idea: str) -> Dict:
        """Crée un plan intelligent avec apprentissage"""
        
        # Analyse avancée
        analysis = self._deep_analyze(idea)
        
        # Génération du plan
        steps = self._generate_intelligent_steps(analysis)
        
        plan = {
            "id": str(uuid.uuid4())[:8],
            "idea": idea,
            "project_type": analysis["type"],
            "complexity": analysis["complexity"],
            "features": analysis["features"],
            "estimated_time": analysis["estimated_time"],
            "technologies": analysis["technologies"],
            "steps": steps,
            "created_at": datetime.now().isoformat(),
            "status": "planning"
        }
        
        # Apprentissage
        self._learn_from_idea(idea, analysis)
        
        print(f"\n📊 VISION PRO - Analyse:")
        print(f"   🎯 Type: {analysis['type']}")
        print(f"   ⭐ Complexité: {analysis['complexity']}/5")
        print(f"   ⏱️ Temps estimé: {analysis['estimated_time']}")
        print(f"   🔧 Technologies: {', '.join(analysis['technologies'])}")
        print(f"   ✨ Fonctionnalités: {', '.join(analysis['features'])}")
        
        return plan
    
    def _deep_analyze(self, idea: str) -> Dict:
        """Analyse approfondie de l'idée"""
        idea_lower = idea.lower()
        
        # Détection du type de projet (élargi)
        type_patterns = {
            "portfolio": ["portfolio", "photographe", "artiste", "galerie", "création"],
            "ecommerce": ["boutique", "e-commerce", "commerce", "vente", "produit", "panier"],
            "blog": ["blog", "article", "post", "actualité", "magazine"],
            "social": ["réseau social", "communauté", "forum", "partage"],
            "api": ["api", "rest", "backend", "service", "microservice"],
            "dashboard": ["dashboard", "tableau de bord", "admin", "statistiques"],
            "crm": ["crm", "client", "relation client", "gestion client"],
            "todo": ["tâche", "task", "todo", "liste", "gestion"],
            "chat": ["chat", "messagerie", "discussion", "talk"],
            "education": ["cours", "formation", "apprentissage", "tutoriel"],
            "health": ["santé", "médical", "bien-être", "fitness"],
            "finance": ["finance", "budget", "dépense", "compte"],
            "games": ["jeu", "game", "quiz", "quizz"]
        }
        
        project_type = "generic"
        for ptype, keywords in type_patterns.items():
            if any(k in idea_lower for k in keywords):
                project_type = ptype
                break
        
        # Estimation de complexité (1-5)
        complexity = 1
        complexity_keywords = {
            2: ["simple", "basique", "minimal"],
            3: ["standard", "classique", "normal"],
            4: ["complexe", "avancé", "complet"],
            5: ["professionnel", "entreprise", "large échelle", "full"]
        }
        for level, words in complexity_keywords.items():
            if any(w in idea_lower for w in words):
                complexity = level
                break
        
        # Détection des fonctionnalités
        features = []
        feature_patterns = {
            "authentification": ["login", "auth", "connexion", "inscription", "compte"],
            "base de données": ["database", "sql", "mongodb", "stockage"],
            "recherche": ["recherche", "search", "filtre"],
            "notifications": ["notification", "alerte", "email"],
            "export": ["export", "pdf", "csv", "excel"],
            "paiement": ["paiement", "payment", "stripe", "paypal"],
            "api externe": ["api externe", "integration", "webhook"],
            "admin panel": ["admin", "administration", "modération"],
            "analytics": ["analytics", "statistiques", "graphique", "rapport"],
            "multilingue": ["multilingue", "traduction", "langue", "i18n"]
        }
        
        for feature, keywords in feature_patterns.items():
            if any(k in idea_lower for k in keywords):
                features.append(feature)
        
        # Technologies recommandées
        techs = self._recommend_technologies(project_type, features)
        
        # Temps estimé (heures)
        estimated_time = complexity * 2 + len(features)
        
        return {
            "type": project_type,
            "complexity": complexity,
            "features": features,
            "technologies": techs,
            "estimated_time": f"{estimated_time}-{estimated_time*2} heures"
        }
    
    def _recommend_technologies(self, project_type: str, features: List[str]) -> List[str]:
        """Recommande les technologies adaptées"""
        base_techs = ["Python/Flask", "HTML/CSS", "JavaScript"]
        
        if "base de données" in features:
            base_techs.append("SQLite/PostgreSQL")
        if "authentification" in features:
            base_techs.append("JWT/OAuth")
        if "api externe" in features:
            base_techs.append("REST API")
        if "paiement" in features:
            base_techs.append("Stripe API")
        if "analytics" in features:
            base_techs.append("Chart.js/D3.js")
        
        return base_techs
    
    def _generate_intelligent_steps(self, analysis: Dict) -> List[Dict]:
        """Génère des étapes intelligentes"""
        steps = []
        
        # Étape 1: Structure de base
        steps.append({
            "id": 1,
            "name": "Initialisation du projet",
            "description": "Création de la structure de base et configuration",
            "files": ["backend.py", "requirements.txt", "config.py"],
            "completed": False
        })
        
        # Étape 2: Base de données (si nécessaire)
        if "base de données" in analysis["features"]:
            steps.append({
                "id": 2,
                "name": "Configuration base de données",
                "description": "Mise en place de SQLAlchemy et modèles",
                "files": ["models.py", "database.py"],
                "completed": False
            })
        
        # Étape 3: Authentification (si nécessaire)
        if "authentification" in analysis["features"]:
            steps.append({
                "id": 3,
                "name": "Système d'authentification",
                "description": "JWT, login, register, middleware",
                "files": ["auth.py", "middleware.py"],
                "completed": False
            })
        
        # Étape 4: API Endpoints
        steps.append({
            "id": 4,
            "name": "Création des endpoints API",
            "description": f"Endpoints CRUD pour {analysis['type']}",
            "files": ["routes.py"],
            "completed": False
        })
        
        # Étape 5: Frontend
        steps.append({
            "id": 5,
            "name": "Interface utilisateur",
            "description": "HTML/CSS/JS moderne et responsive",
            "files": ["index.html", "style.css", "script.js"],
            "completed": False
        })
        
        # Étape 6: Fonctionnalités avancées
        if "recherche" in analysis["features"]:
            steps.append({
                "id": 6,
                "name": "Recherche avancée",
                "description": "Filtres et recherche en temps réel",
                "files": ["search.js"],
                "completed": False
            })
        
        if "analytics" in analysis["features"]:
            steps.append({
                "id": 7,
                "name": "Tableau de bord analytics",
                "description": "Graphiques et statistiques",
                "files": ["dashboard.html", "charts.js"],
                "completed": False
            })
        
        # Étape finale: Documentation
        steps.append({
            "id": len(steps) + 1,
            "name": "Documentation et déploiement",
            "description": "README, guide d'installation, déploiement",
            "files": ["README.md", "DEPLOY.md"],
            "completed": False
        })
        
        return steps
    
    def _learn_from_idea(self, idea: str, analysis: Dict):
        """Apprend de chaque idée analysée"""
        self.patterns["project_types"][analysis["type"]] = self.patterns["project_types"].get(analysis["type"], 0) + 1
        
        for feature in analysis["features"]:
            self.patterns["feature_detection"][feature] = self.patterns["feature_detection"].get(feature, 0) + 1
        
        self.patterns["complexity_patterns"][str(analysis["complexity"])] = self.patterns["complexity_patterns"].get(str(analysis["complexity"]), 0) + 1
        
        self.save_memory()
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques d'apprentissage"""
        return {
            "total_analyses": sum(self.patterns["project_types"].values()),
            "project_types": self.patterns["project_types"],
            "common_features": sorted(self.patterns["feature_detection"].items(), key=lambda x: x[1], reverse=True)[:5],
            "complexity_distribution": self.patterns["complexity_patterns"]
        }
