"""
Designer Agent - DESIGNER PRO
Crée des interfaces modernes avec tous les styles tendance
"""

import os

class Designer:
    def __init__(self):
        self.themes = {
            "glassmorphism": {
                "name": "Glassmorphism",
                "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "card_bg": "rgba(255,255,255,0.2)",
                "backdrop": "blur(10px)",
                "button": "rgba(255,255,255,0.3)",
                "text": "white",
                "border": "1px solid rgba(255,255,255,0.2)"
            },
            "dark_mode": {
                "name": "Dark Mode",
                "bg": "#1a1a2e",
                "card_bg": "rgba(26,26,46,0.9)",
                "backdrop": "blur(10px)",
                "button": "#4facfe",
                "text": "#fff",
                "border": "1px solid rgba(255,255,255,0.1)"
            },
            "minimal": {
                "name": "Minimaliste",
                "bg": "#ffffff",
                "card_bg": "#ffffff",
                "shadow": "0 2px 10px rgba(0,0,0,0.05)",
                "button": "#333",
                "text": "#333",
                "border": "1px solid #eee"
            },
            "gradient": {
                "name": "Gradient",
                "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "card_bg": "rgba(255,255,255,0.95)",
                "button": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                "text": "#333",
                "border": "none"
            }
        }
        
        self.animations = """
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        """
    
    def get_best_style(self, project_type):
        """Choisit le meilleur thème selon le type de projet"""
        if "portfolio" in project_type.lower() or "photographe" in project_type.lower():
            return self.themes["glassmorphism"]
        elif "ecommerce" in project_type.lower() or "boutique" in project_type.lower():
            return self.themes["minimal"]
        elif "dark" in project_type.lower():
            return self.themes["dark_mode"]
        return self.themes["gradient"]
    
    def generate_css(self, project_type, style=None):
        """Génère du CSS moderne"""
        if style is None:
            style = self.get_best_style(project_type)
        
        base_css = f"""
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: {style["bg"]};
            min-height: 100vh;
            padding: 20px;
            color: {style["text"]};
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{
            background: {style["card_bg"]};
            backdrop-filter: {style.get("backdrop", "none")};
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: {style.get("shadow", "0 20px 40px rgba(0,0,0,0.1)")};
            border: {style.get("border", "none")};
            transition: transform 0.3s;
            animation: fadeIn 0.5s ease;
        }}
        button {{
            background: {style["button"]};
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
        }}
        input, textarea {{
            width: 100%;
            padding: 12px;
            border: {style.get("border", "2px solid #e0e0e0")};
            border-radius: 16px;
            background: rgba(255,255,255,0.9);
        }}
        """
        return base_css + self.animations
    
    def create_modern_interface(self, project_type, idea):
        """Crée une interface moderne complète"""
        style = self.get_best_style(project_type)
        css = self.generate_css(project_type, style)
        
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORVIA - {idea[:40]}</title>
    <style>
        {css}
        
        .hero {{
            text-align: center;
            padding: 60px 20px;
        }}
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: rgba(102,126,234,0.2);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
        }}
        .stat-card h3 {{
            font-size: 2rem;
        }}
        .input-group {{
            display: flex;
            gap: 15px;
            margin: 20px 0;
        }}
        .items-list {{
            margin-top: 20px;
        }}
        .item {{
            background: rgba(0,0,0,0.05);
            border-radius: 16px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2rem; }}
            .input-group {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card fade-in">
            <div class="hero">
                <h1>✨ {idea[:60]}</h1>
                <p>Application générée par ORVIA PRO</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card"><h3 id="total">0</h3><p>Éléments</p></div>
                <div class="stat-card"><h3 id="apiStatus">...</h3><p>API</p></div>
            </div>
            
            <div class="input-group">
                <input type="text" id="itemInput" placeholder="Ajouter un élément..." onkeypress="if(event.key==='Enter') addItem()">
                <button onclick="addItem()">➕ Ajouter</button>
            </div>
            
            <div id="itemsList" class="items-list">
                <div style="text-align:center; padding:40px;">✨ Aucun élément. Ajoutez-en un !</div>
            </div>
        </div>
    </div>
    
    <script>
        const API_URL = 'http://127.0.0.1:5002';
        let items = [];
        
        async function checkAPI() {{
            try {{
                const response = await fetch(API_URL + '/api/status');
                if (response.ok) {{
                    document.getElementById('apiStatus').textContent = '✅ Online';
                    return true;
                }}
            }} catch(e) {{
                document.getElementById('apiStatus').textContent = '❌ Offline';
            }}
            return false;
        }}
        
        async function loadItems() {{
            try {{
                const response = await fetch(API_URL + '/api/items');
                const data = await response.json();
                items = data.items || [];
                document.getElementById('total').textContent = items.length;
                renderItems();
            }} catch(e) {{
                console.log('Mode démo');
            }}
        }}
        
        function renderItems() {{
            const container = document.getElementById('itemsList');
            if (items.length === 0) {{
                container.innerHTML = '<div style="text-align:center; padding:40px;">📭 Aucun élément. Ajoutez-en un !</div>';
                return;
            }}
            let html = '';
            for (let i = 0; i < items.length; i++) {{
                const item = items[i];
                const value = item.value || item.title || item.data;
                html += `
                    <div class="item slide-in">
                        <div>
                            <strong>#{item.id}</strong><br>
                            ${{escapeHtml(value)}}<br>
                            <small style="opacity:0.6;">📅 ${{new Date(item.created_at).toLocaleString()}}</small>
                        </div>
                        <button onclick="deleteItem(${{item.id}})" style="background:#dc3545; color:white; border:none; padding:5px 15px; border-radius:20px;">🗑️</button>
                    </div>
                `;
            }}
            container.innerHTML = html;
        }}
        
        async function addItem() {{
            const input = document.getElementById('itemInput');
            const value = input.value.trim();
            if (!value) return;
            
            try {{
                const response = await fetch(API_URL + '/api/items', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ value: value }})
                }});
                if (response.ok) {{
                    input.value = '';
                    loadItems();
                }}
            }} catch(e) {{
                const newItem = {{ id: Date.now(), value: value, created_at: new Date().toISOString() }};
                items.push(newItem);
                document.getElementById('total').textContent = items.length;
                renderItems();
                input.value = '';
            }}
        }}
        
        async function deleteItem(id) {{
            try {{
                await fetch(API_URL + '/api/items/' + id, {{ method: 'DELETE' }});
                loadItems();
            }} catch(e) {{
                items = items.filter(i => i.id !== id);
                document.getElementById('total').textContent = items.length;
                renderItems();
            }}
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        checkAPI();
        loadItems();
        setInterval(() => {{ checkAPI(); loadItems(); }}, 3000);
    </script>
</body>
</html>'''
