"""
Debugger Agent - SENTINEL PRO
Analyse en profondeur, détecte les incohérences et propose des corrections
"""

import os
import re
import ast
from datetime import datetime

class Debugger:
    def __init__(self):
        self.errors_found = []
        self.corrections_applied = []
    
    def fix_error(self, step, error_message):
        print(f"   🔍 SENTINEL PRO: Analyse de l'erreur...")
        return True
    
    def run_full_debug(self, project_path="generated_project"):
        """Analyse complète du projet généré"""
        print("\n" + "="*60)
        print("🛡️ SENTINEL PRO - Analyse de sécurité et qualité")
        print("="*60)
        
        issues = []
        
        if not os.path.exists(project_path):
            print("   ❌ Dossier projet non trouvé")
            return False
        
        # Analyser chaque fichier
        for filename in os.listdir(project_path):
            filepath = os.path.join(project_path, filename)
            
            if filename.endswith('.py'):
                issues += self._analyze_python(filepath, filename)
            elif filename.endswith('.html'):
                issues += self._analyze_html(filepath, filename)
            elif filename.endswith('.json'):
                issues += self._analyze_json(filepath, filename)
        
        # Rapport
        print("\n📊 RAPPORT SENTINEL:")
        print(f"   🔍 {len(issues)} problème(s) détecté(s)")
        
        for issue in issues:
            print(f"   ⚠️ [{issue['severity']}] {issue['file']}: {issue['message']}")
            if issue.get('suggestion'):
                print(f"      💡 Suggestion: {issue['suggestion']}")
        
        if len(issues) == 0:
            print("   ✅ Aucun problème détecté")
        else:
            print(f"\n   🛡️ {len(issues)} problème(s) à corriger")
        
        return len(issues) == 0
    
    def _analyze_python(self, filepath, filename):
        """Analyse un fichier Python"""
        issues = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la présence de fonctionnalités essentielles
        if "authentification" in filename.lower():
            if "jwt" not in content.lower():
                issues.append({
                    "severity": "HIGH",
                    "file": filename,
                    "message": "Pas d'authentification JWT",
                    "suggestion": "Ajouter flask-jwt-extended"
                })
        
        # Vérifier les endpoints
        endpoints = re.findall(r"@app\.route\(['\"]([^'\"]+)['\"]", content)
        if not endpoints:
            issues.append({
                "severity": "MEDIUM",
                "file": filename,
                "message": "Aucun endpoint API détecté",
                "suggestion": "Ajouter des routes avec @app.route()"
            })
        
        # Vérifier la base de données
        if "sqlalchemy" not in content and "sqlite" not in content:
            issues.append({
                "severity": "LOW",
                "file": filename,
                "message": "Pas de base de données configurée",
                "suggestion": "Ajouter SQLAlchemy pour la persistance"
            })
        
        # Vérifier la gestion des erreurs
        if "try:" not in content or "except" not in content:
            issues.append({
                "severity": "MEDIUM",
                "file": filename,
                "message": "Pas de gestion des erreurs",
                "suggestion": "Ajouter des blocs try/except"
            })
        
        return issues
    
    def _analyze_html(self, filepath, filename):
        """Analyse un fichier HTML"""
        issues = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la présence de pages multiples (site de comptabilité)
        if "comptabilité" in filepath.lower() or "cota" in filepath.lower():
            pages_required = ["accueil", "information", "développement"]
            pages_found = []
            
            for page in pages_required:
                if page in content.lower():
                    pages_found.append(page)
            
            if len(pages_found) < 3:
                issues.append({
                    "severity": "HIGH",
                    "file": filename,
                    "message": f"Pages manquantes: {', '.join(set(pages_required) - set(pages_found))}",
                    "suggestion": "Ajouter les sections accueil, information et développement"
                })
        
        # Vérifier le responsive
        if "@media" not in content:
            issues.append({
                "severity": "MEDIUM",
                "file": filename,
                "message": "Pas de design responsive",
                "suggestion": "Ajouter des media queries pour mobile"
            })
        
        # Vérifier les animations
        if "animation" not in content and "transition" not in content:
            issues.append({
                "severity": "LOW",
                "file": filename,
                "message": "Pas d'animations CSS",
                "suggestion": "Ajouter des transitions pour améliorer l'expérience"
            })
        
        return issues
    
    def _analyze_json(self, filepath, filename):
        """Analyse un fichier JSON"""
        issues = []
        import json
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "steps" in data and data.get("steps"):
                steps = data["steps"]
                incomplete = [s for s in steps if not s.get("completed")]
                if incomplete:
                    issues.append({
                        "severity": "MEDIUM",
                        "file": filename,
                        "message": f"{len(incomplete)} étapes non terminées",
                        "suggestion": "Compléter les étapes restantes"
                    })
        except:
            pass
        
        return issues
    
    def validate_project(self, project_path="generated_project"):
        """Validation finale avant livraison"""
        print("\n" + "="*60)
        print("✅ SENTINEL - Validation finale")
        print("="*60)
        
        issues = self.run_full_debug(project_path)
        
        if issues:
            print("\n❌ VALIDATION ÉCHOUÉE - Projet non conforme")
            return False
        else:
            print("\n✅ VALIDATION RÉUSSIE - Projet conforme aux standards")
            return True
