"""
CV Studio - Generador de CVs con RenderCV
"""
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
import yaml
import subprocess
import os
import tempfile
import shutil

app = Flask(__name__)

THEMES = ['classic', 'moderncv', 'sb2nov', 'engineeringclassic', 'engineeringresumes']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')

@app.route('/')
def index():
    return render_template('index.html', themes=THEMES)

@app.route('/preview/<theme>')
def get_preview(theme):
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

@app.route('/generate', methods=['POST'])
def generate_cv():
    """Generar PDF del CV"""
    data = request.json
    
    # Construir estructura YAML
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
    social = []
    if data.get('linkedin'):
        social.append({'network': 'LinkedIn', 'username': data['linkedin']})
    if data.get('github'):
        social.append({'network': 'GitHub', 'username': data['github']})
    if social:
        cv_data['cv']['social_networks'] = social
    
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
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    yaml_path = os.path.join(temp_dir, 'cv.yaml')
    
    try:
        # Guardar YAML
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(cv_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        # Ejecutar rendercv
        result = subprocess.run(
            ['rendercv', 'render', yaml_path],
            capture_output=True,
            text=True,
            cwd=temp_dir,
            timeout=60
        )
        
        if result.returncode != 0:
            return jsonify({'error': f'Error al generar: {result.stderr}'}), 500
        
        # Buscar PDF generado
        output_dir = os.path.join(temp_dir, 'rendercv_output')
        if os.path.exists(output_dir):
            pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
            if pdf_files:
                pdf_path = os.path.join(output_dir, pdf_files[0])
                name = data.get('name', 'CV').replace(' ', '_')
                return send_file(
                    pdf_path, 
                    as_attachment=True, 
                    download_name=f'{name}_CV.pdf',
                    mimetype='application/pdf'
                )
        
        return jsonify({'error': 'No se generó el PDF'}), 500
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout al generar el PDF'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
