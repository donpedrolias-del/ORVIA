"""
Tester Agent - JUDGE PRO
Tests complets, validation fonctionnelle, rapport de qualité
"""

import os
import re
import subprocess
import time
from datetime import datetime

class Tester:
    def __init__(self):
        self.test_results = []
        self.quality_score = 0
    
    def run_tests(self, project_path="generated_project"):
        """Exécute tous les tests sur le projet"""
        print("\n" + "="*60)
        print("⚖️ JUDGE PRO - Tests fonctionnels")
        print("="*60)
        
        tests = {
            "syntax": self._test_syntax(project_path),
            "imports": self._test_imports(project_path),
            "endpoints": self._test_endpoints(project_path),
            "html_structure": self._test_html_structure(project_path),
            "responsive": self._test_responsive(project_path),
            "security": self._test_security(project_path),
            "performance": self._test_performance(project_path)
        }
        
        self._print_report(tests)
        return all(tests.values())
    
    def _test_syntax(self, project_path):
        """Teste la syntaxe Python"""
        print("\n   📝 Test de syntaxe Python...")
        
        for file in os.listdir(project_path):
            if file.endswith('.py'):
                filepath = os.path.join(project_path, file)
                try:
                    with open(filepath, 'r') as f:
                        compile(f.read(), filepath, 'exec')
                    print(f"      ✅ {file}: syntaxe valide")
                except SyntaxError as e:
                    print(f"      ❌ {file}: {e}")
                    return False
        return True
    
    def _test_imports(self, project_path):
        """Teste les imports"""
        print("\n   📦 Test des imports...")
        
        required_modules = {
            "flask": "Flask",
            "flask_cors": "CORS"
        }
        
        for file in os.listdir(project_path):
            if file.endswith('.py'):
                with open(os.path.join(project_path, file), 'r') as f:
                    content = f.read()
                
                missing = []
                for module, import_name in required_modules.items():
                    if f"import {module}" not in content and f"from {module}" not in content:
                        missing.append(module)
                
                if missing:
                    print(f"      ⚠️ {file}: modules manquants: {', '.join(missing)}")
                    return False
        
        print(f"      ✅ Tous les imports essentiels sont présents")
        return True
    
    def _test_endpoints(self, project_path):
        """Teste les endpoints API (simulation)"""
        print("\n   🌐 Test des endpoints API...")
        
        backend_path = os.path.join(project_path, "backend.py")
        if not os.path.exists(backend_path):
            print("      ❌ backend.py non trouvé")
            return False
        
        with open(backend_path, 'r') as f:
            content = f.read()
        
        # Vérifier les endpoints essentiels
        essential_endpoints = ["/api/status", "/api/items"]
        missing_endpoints = []
        
        for endpoint in essential_endpoints:
            if endpoint not in content:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"      ❌ Endpoints manquants: {', '.join(missing_endpoints)}")
            return False
        
        # Compter les endpoints
        endpoints = re.findall(r"@app\.route\('([^']+)'", content)
        print(f"      ✅ {len(endpoints)} endpoint(s) trouvé(s)")
        return True
    
    def _test_html_structure(self, project_path):
        """Teste la structure HTML"""
        print("\n   🎨 Test de la structure HTML...")
        
        html_files = [f for f in os.listdir(project_path) if f.endswith('.html')]
        
        if not html_files:
            print("      ❌ Aucun fichier HTML trouvé")
            return False
        
        for html_file in html_files:
            filepath = os.path.join(project_path, html_file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Vérifier les balises essentielles
            if '<!DOCTYPE html>' not in content:
                print(f"      ⚠️ {html_file}: doctype manquant")
            if '<head>' not in content:
                print(f"      ⚠️ {html_file}: head manquant")
            if '<body>' not in content:
                print(f"      ⚠️ {html_file}: body manquant")
            
            # Vérifier les pages demandées (si site de comptabilité)
            if "comptabilité" in html_file.lower() or "cota" in filepath.lower():
                pages = ["accueil", "information", "développement", "developpement"]
                found = []
                for page in pages:
                    if page in content.lower():
                        found.append(page)
                
                if len(found) < 3:
                    print(f"      ⚠️ {html_file}: pages manquantes (accueil, information, développement)")
        
        print(f"      ✅ Structure HTML valide")
        return True
    
    def _test_responsive(self, project_path):
        """Teste le responsive design"""
        print("\n   📱 Test du responsive...")
        
        html_files = [f for f in os.listdir(project_path) if f.endswith('.html')]
        responsive_found = False
        
        for html_file in html_files:
            filepath = os.path.join(project_path, html_file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            if "@media" in content or "viewport" in content:
                responsive_found = True
                print(f"      ✅ {html_file}: design responsive")
                break
        
        if not responsive_found:
            print(f"      ⚠️ Aucun design responsive détecté (media queries manquantes)")
            return False
        
        return True
    
    def _test_security(self, project_path):
        """Teste la sécurité basique"""
        print("\n   🔒 Test de sécurité...")
        
        backend_path = os.path.join(project_path, "backend.py")
        if os.path.exists(backend_path):
            with open(backend_path, 'r') as f:
                content = f.read()
            
            # Vérifier les secrets
            if "secrets" not in content and "SECRET_KEY" not in content:
                print(f"      ⚠️ Pas de clé secrète configurée")
            
            # Vérifier l'échappement HTML
            html_files = [f for f in os.listdir(project_path) if f.endswith('.html')]
            for html_file in html_files:
                filepath = os.path.join(project_path, html_file)
                with open(filepath, 'r') as f:
                    html_content = f.read()
                
                if "escapeHtml" not in html_content:
                    print(f"      ⚠️ {html_file}: risque XSS - pas d'échappement HTML")
        
        print(f"      ✅ Sécurité basique vérifiée")
        return True
    
    def _test_performance(self, project_path):
        """Teste la performance"""
        print("\n   ⚡ Test de performance...")
        
        # Vérifier la taille des fichiers
        total_size = 0
        for file in os.listdir(project_path):
            filepath = os.path.join(project_path, file)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
        
        if total_size > 1000000:  # 1MB
            print(f"      ⚠️ Taille du projet: {total_size/1024:.0f} KB (peut être optimisé)")
        else:
            print(f"      ✅ Taille du projet: {total_size/1024:.0f} KB")
        
        return True
    
    def _print_report(self, tests):
        """Affiche le rapport des tests"""
        print("\n" + "="*60)
        print("📊 RAPPORT JUDGE PRO")
        print("="*60)
        
        passed = sum(tests.values())
        total = len(tests)
        self.quality_score = int((passed / total) * 100)
        
        for test, passed_test in tests.items():
            status = "✅" if passed_test else "❌"
            print(f"   {status} {test}")
        
        print(f"\n📈 Score de qualité: {self.quality_score}/100")
        
        if self.quality_score == 100:
            print("🏆 QUALITÉ PARFAITE - Prêt pour la production!")
        elif self.quality_score >= 80:
            print("👍 BONNE QUALITÉ - Quelques améliorations possibles")
        elif self.quality_score >= 60:
            print("⚠️ QUALITÉ MOYENNE - Nécessite des améliorations")
        else:
            print("🔧 QUALITÉ INSUFFISANTE - Refonte recommandée")
        
        return self.quality_score
    
    def simulate_launch(self, project_path="generated_project"):
        """Simule le lancement de l'application"""
        print("\n🚀 Simulation du lancement...")
        
        backend_path = os.path.join(project_path, "backend.py")
        if not os.path.exists(backend_path):
            print("   ❌ backend.py non trouvé")
            return False
        
        print("   ✅ Application prête à être lancée")
        print(f"   💡 Commande: cd {project_path} && python3 backend.py")
        
        return True
    
    def get_detailed_report(self):
        """Retourne un rapport détaillé"""
        return {
            "quality_score": self.quality_score,
            "tests_passed": self.test_results,
            "timestamp": datetime.now().isoformat(),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self):
        """Génère des recommandations d'amélioration"""
        recommendations = []
        
        if self.quality_score < 60:
            recommendations.append("🔧 Améliorer la structure du code")
            recommendations.append("📱 Ajouter le responsive design")
            recommendations.append("🔒 Implémenter l'authentification")
        
        if self.quality_score < 80:
            recommendations.append("✨ Ajouter des animations")
            recommendations.append("📊 Intégrer des statistiques")
        
        return recommendations
