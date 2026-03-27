"""
Memory Agent - MÉMOIRE
Se souvient de toutes les conversations et projets
"""

import os
import json
import pickle
from datetime import datetime

class Memory:
    def __init__(self):
        # Chemin corrigé : fichier à la racine du projet
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.memory_file = os.path.join(base_dir, "orvia_memory.pkl")
        self.conversations = []
        self.projects = []
        self.current_context = {}
        self.load_memory()
    
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'rb') as f:
                    data = pickle.load(f)
                    self.conversations = data.get("conversations", [])
                    self.projects = data.get("created_apps", [])
                    self.current_context = data.get("context", {})
                print(f"🧠 MÉMOIRE: {len(self.conversations)} conversations, {len(self.projects)} projets")
            except:
                pass
    
    def save_memory(self):
        data = {
            "conversations": self.conversations,
            "created_apps": self.projects,
            "context": self.current_context,
            "last_update": datetime.now().isoformat()
        }
        with open(self.memory_file, 'wb') as f:
            pickle.dump(data, f)
    
    def add_conversation(self, user_message, orvia_response, context=None):
        entry = {
            "user": user_message,
            "orvia": orvia_response,
            "timestamp": datetime.now().isoformat(),
            "context": context or self.current_context.copy()
        }
        self.conversations.append(entry)
        if len(self.conversations) > 100:
            self.conversations = self.conversations[-100:]
        self.save_memory()
    
    def add_project(self, project_id, idea):
        project = {
            "id": project_id,
            "idea": idea,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.projects.append(project)
        self.current_context["last_project"] = project_id
        self.current_context["last_idea"] = idea
        self.save_memory()
    
    def update_context(self, key, value):
        self.current_context[key] = value
        self.save_memory()
    
    def get_last_conversations(self, count=5):
        return self.conversations[-count:] if self.conversations else []
    
    def get_last_project(self):
        if self.projects:
            return self.projects[-1]
        return None
    
    def get_projects_list(self):
        return self.projects
    
    def get_context_summary(self):
        summary = ""
        if self.current_context.get("last_idea"):
            summary += f"📝 Dernier projet: {self.current_context['last_idea']}\n"
        if self.current_context.get("working_on"):
            summary += f"🔧 Travail en cours: {self.current_context['working_on']}\n"
        if self.projects:
            summary += f"📁 Total projets: {len(self.projects)}\n"
        if self.conversations:
            summary += f"💬 Conversations: {len(self.conversations)}\n"
        return summary
    
    def recall(self):
        summary = self.get_context_summary()
        if summary:
            return f"🧠 **MÉMOIRE**\n\n{summary}\nJe me souviens de tout !"
        return "🧠 Je n'ai pas encore de souvenirs. Commençons à créer !"
