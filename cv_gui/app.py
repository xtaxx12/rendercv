"""
CV Studio - Generador de CVs con RenderCV
Versión para Vercel (genera YAML para usar con RenderCV CLI)
"""
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import yaml
import os

app = Flask(__name__)

THEMES = ['classic', 'moderncv', 'sb2nov', 'engineeringclassic', 'engineeringresumes']

# Ruta a los ejemplos (para previews)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')

@app.route('/')
def index():
    return render_template('index.html', themes=THEMES)

@app.route('/preview/<theme>')
def get_preview(theme):
    """Servir el PDF de preview de cada tema"""
    theme_map = {
        'classic': 'John_Doe_ClassicTheme_CV.pdf',
        'moderncv': 'John_Doe_ModerncvTheme_CV.pdf',
        'sb2nov': 'John_Doe_Sb2novTheme_CV.pdf',
        'engineeringclassic': 'John_Doe_EngineeringclassicTheme_CV.pdf',
        'engineeringresumes': 'John_Doe_EngineeringresumesTheme_CV.pdf'
    }
    filename = theme_map.get(theme)
    if filename:
        filepath = os.path.join(EXAMPLES_DIR, filename)
        if os.path.exists(filepath):
            return send_from_directory(EXAMPLES_DIR, filename, mimetype='application/pdf')
    return jsonify({'error': 'Preview no encontrado'}), 404

@app.route('/generate-yaml', methods=['POST'])
def generate_yaml():
    """Generar y devolver el archivo YAML"""
    data = request.json
    
    cv_data = {
        'cv': {
            'name': data.get('name', ''),
        },
        'design': {
            'theme': data.get('theme', 'classic')
        },
        'locale': {
            'language': data.get('language', 'spanish')
        }
    }
    
    # Campos opcionales
    if data.get('headline'):
        cv_data['cv']['headline'] = data['headline']
    if data.get('location'):
        cv_data['cv']['location'] = data['location']
    if data.get('email'):
        cv_data['cv']['email'] = data['email']
    if data.get('phone'):
        cv_data['cv']['phone'] = data['phone']
    if data.get('website'):
        cv_data['cv']['website'] = data['website']
    
    # Redes sociales
    social_networks = []
    if data.get('linkedin'):
        social_networks.append({'network': 'LinkedIn', 'username': data['linkedin']})
    if data.get('github'):
        social_networks.append({'network': 'GitHub', 'username': data['github']})
    if social_networks:
        cv_data['cv']['social_networks'] = social_networks
    
    # Secciones
    sections = {}
    if data.get('summary'):
        sections['resumen'] = data['summary']
    if data.get('experience'):
        sections['experiencia'] = data['experience']
    if data.get('education'):
        sections['educación'] = data['education']
    if data.get('projects'):
        sections['proyectos'] = data['projects']
    if data.get('skills'):
        sections['skills'] = data['skills']
    
    if sections:
        cv_data['cv']['sections'] = sections
    
    # Generar YAML
    yaml_content = yaml.dump(cv_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    # Nombre del archivo
    name = data.get('name', 'mi_cv').replace(' ', '_')
    filename = f"{name}_CV.yaml"
    
    return Response(
        yaml_content,
        mimetype='text/yaml',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

# Para Vercel
app = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
