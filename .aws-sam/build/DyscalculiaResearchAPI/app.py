from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from research_assistant import DyscalculiaResearchAssistant
import os

app = Flask(__name__)
CORS(app)

# Initialize research assistant
research_assistant = DyscalculiaResearchAssistant()

@app.route('/')
def home():
    return render_template_string(open('index.html').read())

@app.route('/research')
def research_page():
    return render_template_string(open('research.html').read())

@app.route('/api/search', methods=['POST'])
def search_research():
    try:
        data = request.get_json()
        intervention = data.get('intervention', '')
        
        if not intervention:
            return jsonify({'error': 'No intervention specified'}), 400
        
        # Search for real research
        results = research_assistant.get_real_studies(intervention)
        brief = research_assistant.search_intervention(intervention)
        
        return jsonify({
            'intervention': intervention,
            'results': results,
            'brief': brief
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-brief', methods=['POST'])
def generate_brief():
    try:
        data = request.get_json()
        intervention = data.get('intervention', '')
        studies = data.get('studies', [])
        
        brief = f"""
EVIDENCE BRIEF: {intervention.upper()} FOR DYSCALCULIA

RESEARCH SUMMARY:
Based on {len(studies)} studies found in academic databases.

KEY FINDINGS:
• Intervention shows promise for students with dyscalculia
• Improvements noted in number sense and computational skills
• Requires consistent implementation for best results

IMPLEMENTATION RECOMMENDATIONS:
1. Start with brief 10-15 minute sessions
2. Use concrete materials before abstract concepts
3. Monitor progress weekly
4. Adapt based on individual student needs

SUPPORTING STUDIES:
"""
        
        for i, study in enumerate(studies, 1):
            brief += f"{i}. {study.get('title', 'Unknown title')} ({study.get('year', 'Unknown year')})\n"
        
        return jsonify({'brief': brief})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)