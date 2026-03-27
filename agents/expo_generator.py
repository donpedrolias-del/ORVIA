"""
Expo Generator - Crée des applications React Native
"""

import os
import json
from datetime import datetime

class ExpoGenerator:
    def __init__(self):
        self.output_dir = "generated_expo_app"
    
    def generate_expo_app(self, idea, project_id):
        """Génère une application React Native pour Expo"""
        
        project_path = os.path.join("generated_projects", project_id)
        os.makedirs(project_path, exist_ok=True)
        
        # Extraire le nom de l'application
        app_name = idea[:30].replace(" ", "_").replace("'", "").lower()
        
        # 1. Créer app.json (configuration Expo)
        app_config = {
            "expo": {
                "name": idea[:50],
                "slug": app_name,
                "version": "1.0.0",
                "orientation": "portrait",
                "icon": "./assets/icon.png",
                "userInterfaceStyle": "light",
                "splash": {
                    "image": "./assets/splash.png",
                    "resizeMode": "contain",
                    "backgroundColor": "#ffffff"
                },
                "assetBundlePatterns": ["**/*"],
                "ios": {
                    "supportsTablet": True,
                    "bundleIdentifier": f"com.orvia.{app_name}"
                },
                "android": {
                    "adaptiveIcon": {
                        "foregroundImage": "./assets/adaptive-icon.png",
                        "backgroundColor": "#ffffff"
                    },
                    "package": f"com.orvia.{app_name}"
                },
                "web": {
                    "favicon": "./assets/favicon.png"
                },
                "extra": {
                    "eas": {
                        "projectId": f"orvia-{project_id}"
                    }
                }
            }
        }
        
        with open(os.path.join(project_path, "app.json"), 'w') as f:
            json.dump(app_config, f, indent=2)
        
        # 2. Créer App.js (composant principal)
        app_js = f'''import {{ StatusBar }} from 'expo-status-bar';
import {{ StyleSheet, Text, View, TextInput, TouchableOpacity, FlatList, SafeAreaView }} from 'react-native';
import {{ useState, useEffect }} from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function App() {{
  const [items, setItems] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);

  // Charger les données sauvegardées
  useEffect(() => {{
    loadItems();
  }}, []);

  const loadItems = async () => {{
    try {{
      const saved = await AsyncStorage.getItem('@orvia_items');
      if (saved !== null) {{
        setItems(JSON.parse(saved));
      }}
    }} catch (error) {{
      console.error('Erreur de chargement:', error);
    }} finally {{
      setLoading(false);
    }}
  }};

  const saveItems = async (newItems) => {{
    try {{
      await AsyncStorage.setItem('@orvia_items', JSON.stringify(newItems));
    }} catch (error) {{
      console.error('Erreur de sauvegarde:', error);
    }}
  }};

  const addItem = () => {{
    if (inputText.trim() === '') return;
    const newItem = {{
      id: Date.now().toString(),
      text: inputText.trim(),
      createdAt: new Date().toISOString()
    }};
    const newItems = [newItem, ...items];
    setItems(newItems);
    saveItems(newItems);
    setInputText('');
  }};

  const deleteItem = (id) => {{
    const newItems = items.filter(item => item.id !== id);
    setItems(newItems);
    saveItems(newItems);
  }};

  const renderItem = ({{ item }}) => (
    <View style={styles.itemContainer}>
      <View style={styles.itemContent}>
        <Text style={styles.itemText}>{item.text}</Text>
        <Text style={styles.itemDate}>
          {{new Date(item.createdAt).toLocaleDateString()}}
        </Text>
      </View>
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => deleteItem(item.id)}>
        <Text style={styles.deleteButtonText}>🗑️</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {{
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>🚀 ORVIA prépare ton application...</Text>
      </View>
    );
  }}

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>✨ {idea[:40]}</Text>
        <Text style={styles.subtitle}>Généré par ORVIA</Text>
      </View>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Ajouter un élément..."
          value={inputText}
          onChangeText={setInputText}
          onSubmitEditing={addItem}
        />
        <TouchableOpacity style={styles.addButton} onPress={addItem}>
          <Text style={styles.addButtonText}>➕</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={items}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.listContainer}
        ListEmptyComponent={
          <Text style={styles.emptyText}>📭 Aucun élément. Ajoute-en un !</Text>
        }
      />

      <StatusBar style="auto" />
    </SafeAreaView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#f5f5f5',
  }},
  centerContainer: {{
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#667eea',
  }},
  header: {{
    backgroundColor: '#667eea',
    padding: 20,
    paddingTop: 50,
    alignItems: 'center',
  }},
  title: {{
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  }},
  subtitle: {{
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 5,
  }},
  inputContainer: {{
    flexDirection: 'row',
    padding: 15,
    backgroundColor: 'white',
    marginHorizontal: 15,
    marginTop: 15,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {{ width: 0, height: 2 }},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  }},
  input: {{
    flex: 1,
    fontSize: 16,
    padding: 10,
  }},
  addButton: {{
    backgroundColor: '#667eea',
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  }},
  addButtonText: {{
    fontSize: 24,
    color: 'white',
  }},
  listContainer: {{
    padding: 15,
  }},
  itemContainer: {{
    flexDirection: 'row',
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: {{ width: 0, height: 1 }},
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  }},
  itemContent: {{
    flex: 1,
  }},
  itemText: {{
    fontSize: 16,
    color: '#333',
  }},
  itemDate: {{
    fontSize: 10,
    color: '#999',
    marginTop: 5,
  }},
  deleteButton: {{
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 10,
  }},
  deleteButtonText: {{
    fontSize: 20,
  }},
  emptyText: {{
    textAlign: 'center',
    color: '#999',
    marginTop: 50,
  }},
  loadingText: {{
    color: 'white',
    fontSize: 16,
  }},
}});
'''
        
        with open(os.path.join(project_path, "App.js"), 'w') as f:
            f.write(app_js)
        
        # 3. Créer package.json
        package_json = {
            "name": app_name,
            "version": "1.0.0",
            "main": "node_modules/expo/AppEntry.js",
            "scripts": {
                "start": "expo start",
                "android": "expo start --android",
                "ios": "expo start --ios",
                "web": "expo start --web"
            },
            "dependencies": {
                "expo": "~51.0.0",
                "expo-status-bar": "~1.12.0",
                "react": "18.2.0",
                "react-native": "0.74.0",
                "@react-native-async-storage/async-storage": "1.23.0"
            }
        }
        
        with open(os.path.join(project_path, "package.json"), 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # 4. Créer README pour Expo
        readme = f"""# {idea[:50]}

## Application générée par ORVIA pour Expo

### Installation

```bash
cd {project_id}
npm install
