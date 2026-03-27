"""
Dictionnaire intelligent - MÉMOIRE DES MOTS
Apprend et se souvient de tous les mots et expressions
"""

import json
import os
from datetime import datetime

class Dictionary:
    def __init__(self):
        self.dict_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "orvia_dictionary.json")
        self.words = {}
        self.expressions = {}
        self.synonyms = {}
        self.categories = {}
        self.load_dictionary()
    
    def load_dictionary(self):
        """Charge le dictionnaire existant"""
        if os.path.exists(self.dict_file):
            try:
                with open(self.dict_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.words = data.get("words", {})
                    self.expressions = data.get("expressions", {})
                    self.synonyms = data.get("synonyms", {})
                    self.categories = data.get("categories", {})
                print(f"📚 Dictionnaire chargé: {len(self.words)} mots, {len(self.expressions)} expressions")
            except:
                self._init_default_dictionary()
        else:
            self._init_default_dictionary()
    
    def _init_default_dictionary(self):
        """Initialise le dictionnaire avec les mots de base"""
        # Mots de création
        self.words["crée"] = {"category": "action", "meaning": "créer", "synonyms": ["créer", "générer", "fabriquer"]}
        self.words["génère"] = {"category": "action", "meaning": "générer", "synonyms": ["crée", "produire"]}
        self.words["site"] = {"category": "type", "meaning": "site web", "synonyms": ["application", "web", "page"]}
        self.words["app"] = {"category": "type", "meaning": "application", "synonyms": ["application", "logiciel"]}
        self.words["portfolio"] = {"category": "projet", "meaning": "site portfolio", "synonyms": ["galerie", "art"]}
        self.words["ecommerce"] = {"category": "projet", "meaning": "boutique en ligne", "synonyms": ["boutique", "commerce"]}
        self.words["blog"] = {"category": "projet", "meaning": "site de blog", "synonyms": ["article", "actualité"]}
        self.words["todo"] = {"category": "projet", "meaning": "liste de tâches", "synonyms": ["tâches", "tasks"]}
        
        # Catégories de projets
        self.categories["ecommerce"] = ["boutique", "commerce", "vente", "produit", "panier", "shop"]
        self.categories["portfolio"] = ["portfolio", "photographe", "artiste", "galerie", "création", "oeuvre", "art"]
        self.categories["blog"] = ["blog", "article", "actualité", "magazine", "post", "nouvelles"]
        self.categories["todo"] = ["tâche", "task", "todo", "liste", "gestion"]
        self.categories["comptabilite"] = ["compta", "finance", "budget", "dépense", "compte", "argent"]
        
        self.save_dictionary()
    
    def save_dictionary(self):
        """Sauvegarde le dictionnaire"""
        data = {
            "words": self.words,
            "expressions": self.expressions,
            "synonyms": self.synonyms,
            "categories": self.categories,
            "last_update": datetime.now().isoformat()
        }
        with open(self.dict_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def learn_word(self, word, category="general", meaning=None):
        """Apprend un nouveau mot"""
        word_lower = word.lower()
        if word_lower not in self.words:
            self.words[word_lower] = {
                "category": category,
                "meaning": meaning or word,
                "learned_at": datetime.now().isoformat(),
                "synonyms": []
            }
            self.save_dictionary()
            return True, f"📖 J'ai appris le mot: {word}"
        return False, f"📖 Je connais déjà: {word}"
    
    def learn_expression(self, expression, meaning):
        """Apprend une nouvelle expression"""
        expr_lower = expression.lower()
        if expr_lower not in self.expressions:
            self.expressions[expr_lower] = {
                "meaning": meaning,
                "learned_at": datetime.now().isoformat()
            }
            self.save_dictionary()
            return True, f"📚 J'ai appris l'expression: {expression}"
        return False, f"📚 Je connais déjà: {expression}"
    
    def learn_category(self, category_name, keywords):
        """Apprend une nouvelle catégorie de projet"""
        if category_name not in self.categories:
            self.categories[category_name] = keywords
            self.save_dictionary()
            return True, f"🎯 Nouvelle catégorie apprise: {category_name}"
        return False, f"🎯 Catégorie déjà existante: {category_name}"
    
    def detect_project_type(self, text):
        """Détecte le type de projet à partir du texte"""
        text_lower = text.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return "generic"
    
    def get_synonyms(self, word):
        """Retourne les synonymes d'un mot"""
        word_lower = word.lower()
        if word_lower in self.words:
            return self.words[word_lower].get("synonyms", [])
        return []
    
    def understand(self, text):
        """Analyse le texte et retourne l'intention"""
        text_lower = text.lower()
        
        # Détection des intentions de création
        creation_words = ["crée", "créer", "génère", "générer", "fais", "fabrique", "construis", "développe", "veux", "aimerais"]
        if any(word in text_lower for word in creation_words):
            project_type = self.detect_project_type(text)
            return {
                "intent": "create",
                "project_type": project_type,
                "confidence": 0.9
            }
        
        # Détection de demande d'apprentissage
        if "apprend" in text_lower or "apprends" in text_lower or "nouveau mot" in text_lower:
            return {
                "intent": "learn",
                "confidence": 0.8
            }
        
        # Détection de demande de dictionnaire
        if "dictionnaire" in text_lower or "vocabulaire" in text_lower or "mots" in text_lower:
            return {
                "intent": "dictionary",
                "confidence": 0.9
            }
        
        # Détection de demande de projets
        if "projet" in text_lower or "mémoire" in text_lower:
            return {
                "intent": "projects",
                "confidence": 0.8
            }
        
        return {
            "intent": "chat",
            "confidence": 0.5
        }
    
    def get_stats(self):
        """Retourne les statistiques du dictionnaire"""
        return {
            "total_words": len(self.words),
            "total_expressions": len(self.expressions),
            "total_categories": len(self.categories),
            "categories_list": list(self.categories.keys())
        }
    
    def get_all_words(self):
        """Retourne tous les mots appris"""
        return list(self.words.keys())
    
    def search_word(self, search):
        """Recherche un mot dans le dictionnaire"""
        results = []
        search_lower = search.lower()
        
        for word, data in self.words.items():
            if search_lower in word:
                results.append({
                    "word": word,
                    "category": data.get("category"),
                    "meaning": data.get("meaning")
                })
        
        return results
