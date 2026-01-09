"""
Interfaz gráfica web para el generador de CVs con RenderCV
"""
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
import yaml
import subprocess
import os
import tempfile
import shutil

app = Flask(__name__)

THEMES = ['classic', 'moderncv', 'sb2nov', 'engineeringclassic', 'engineeringresumes']

# Ruta a los ejemplos
EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'examples')

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
    if filename and os.path.exists(os.path.join(EXAMPLES_DIR, filename)):
        return send_from_directory(EXAMPLES_DIR, filename)
    return jsonify({'error': 'Preview no encontrado'}), 404

@app.route('/generate', methods=['POST'])
def generate_cv():
    data = request.json
    
    # Construir estructura YAML
    cv_data = {
        'cv': {
            'name': data.get('name', ''),
            'headline': data.get('headline', ''),
            'location': data.get('location', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'website': data.get('website', ''),
            'social_networks': [],
            'sections': {}
        },
        'design': {
            'theme': data.get('theme', 'classic')
        },
        'locale': {
            'language': data.get('language', 'spanish')
        }
    }
    
    # Redes sociales
    if data.get('linkedin'):
        cv_data['cv']['social_networks'].append({'network': 'LinkedIn', 'username': data['linkedin']})
    if data.get('github'):
        cv_data['cv']['social_networks'].append({'network': 'GitHub', 'username': data['github']})
    
    # Secciones
    if data.get('summary'):
        cv_data['cv']['sections']['resumen'] = data['summary']
    
    if data.get('experience'):
        cv_data['cv']['sections']['experiencia'] = data['experience']
    
    if data.get('education'):
        cv_data['cv']['sections']['educación'] = data['education']
    
    if data.get('projects'):
        cv_data['cv']['sections']['proyectos'] = data['projects']
    
    if data.get('skills'):
        cv_data['cv']['sections']['skills'] = data['skills']
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    yaml_path = os.path.join(temp_dir, 'cv.yaml')
    
    try:
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(cv_data, f, allow_unicode=True, default_flow_style=False)
        
        # Ejecutar rendercv
        result = subprocess.run(
            ['uv', 'run', 'rendercv', 'render', yaml_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500
        
        # Buscar PDF generado
        output_dir = os.path.join(temp_dir, 'rendercv_output')
        pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
        
        if pdf_files:
            pdf_path = os.path.join(output_dir, pdf_files[0])
            return send_file(pdf_path, as_attachment=True, download_name='mi_cv.pdf')
        
        return jsonify({'error': 'No se generó el PDF'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
