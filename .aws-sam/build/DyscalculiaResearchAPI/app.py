from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Load tools and research data
def load_tools_data():
    try:
        with open('tools_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_research_data():
    try:
        with open('research_metadata.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Static file routes
@app.route('/styles.css')
def styles():
    return send_from_directory('.', 'styles.css')

@app.route('/tools_data.json')
def tools_data():
    return send_from_directory('.', 'tools_data.json')

@app.route('/research_metadata.json')
def research_metadata():
    return send_from_directory('.', 'research_metadata.json')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico')

# Page routes using templates
@app.route('/')
def home():
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        base = f.read()
    with open('templates/home-content.html', 'r', encoding='utf-8') as f:
        content = f.read()
    with open('templates/home-scripts.html', 'r', encoding='utf-8') as f:
        scripts = f.read()
    
    html = base.replace('{{title}}', 'Home')
    html = html.replace('{{content}}', content)
    html = html.replace('{{scripts}}', scripts)
    return html

@app.route('/about')
def about():
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        base = f.read()
    with open('templates/about-content.html', 'r', encoding='utf-8') as f:
        content = f.read()
    with open('templates/about-scripts.html', 'r', encoding='utf-8') as f:
        scripts = f.read()
    
    html = base.replace('{{title}}', 'About')
    html = html.replace('{{content}}', content)
    html = html.replace('{{scripts}}', scripts)
    return html

@app.route('/tool/<tool_id>')
def tool_page(tool_id):
    tools_data = load_tools_data()
    tool = None
    
    for t in tools_data:
        if t.get('id') == tool_id:
            tool = t
            break
    
    if not tool:
        return '<h1>Tool not found</h1>', 404
    
    # Load templates
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        base_template = f.read()
    with open('templates/tool_detail.html', 'r', encoding='utf-8') as f:
        tool_template = f.read()
    
    # Build content
    steps_html = ''.join([f'<li>{step}</li>' for step in tool.get('steps', [])])
    challenges_html = '<ul>' + ''.join([f'<li>{c}</li>' for c in tool.get('challenges', [])]) + '</ul>'
    tags_html = ''.join([f'<span class="tag tool-tag">{tag}</span>' for tag in tool.get('tags', [])])
    
    # Fill templates
    tool_content = tool_template.replace('{{title}}', tool.get('title', ''))
    tool_content = tool_content.replace('{{description}}', tool.get('description', ''))
    tool_content = tool_content.replace('{{age_range}}', tool.get('age_range', ''))
    tool_content = tool_content.replace('{{setting}}', tool.get('setting', ''))
    tool_content = tool_content.replace('{{time_required}}', tool.get('time_required', ''))
    tool_content = tool_content.replace('{{materials}}', tool.get('materials', ''))
    tool_content = tool_content.replace('{{steps}}', steps_html)
    tool_content = tool_content.replace('{{challenges}}', challenges_html)
    tool_content = tool_content.replace('{{tags}}', tags_html)
    
    html = base_template.replace('{{title}}', tool.get('title', ''))
    html = html.replace('{{content}}', tool_content)
    
    return html

# API routes
@app.route('/api/search', methods=['POST'])
def search_research():
    try:
        data = request.get_json()
        intervention = data.get('intervention', '')
        
        if not intervention:
            return jsonify({'error': 'No intervention specified'}), 400
        
        # Mock results for now - matches Lambda behavior
        results = [{
            'title': f'Research on {intervention} for Dyscalculia',
            'authors': 'Sample Authors',
            'year': '2024',
            'summary': f'This study examines the effectiveness of {intervention} interventions for students with dyscalculia.'
        }]
        
        return jsonify({
            'intervention': intervention,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-brief', methods=['POST'])
def generate_brief():
    try:
        data = request.get_json()
        intervention = data.get('intervention', '')
        studies = data.get('studies', [])
        
        brief = f"Evidence brief for {intervention} - functionality coming soon."
        
        return jsonify({'brief': brief})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)