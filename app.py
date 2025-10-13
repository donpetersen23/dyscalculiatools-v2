from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
import html

app = Flask(__name__)
CORS(app)

# Load research metadata
def load_research_data():
    try:
        with open('Research/research_metadata.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.route('/')
def home():
    return render_template_string(open('index.html').read())

@app.route('/styles.css')
def styles():
    return app.response_class(open('styles.css').read(), mimetype='text/css')

@app.route('/array-tool.html')
def array_tool():
    return render_template_string(open('array-tool.html').read())

@app.route('/research')
def research_page():
    return render_template_string(open('research.html').read())

@app.route('/api/search', methods=['POST'])
def search_research():
    try:
        data = request.get_json()
        query = data.get('query', '').lower()
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        # Load and search research data
        research_data = load_research_data()
        results = []
        
        for study in research_data:
            # Search in title, summary, and dyscalculia_relevance
            searchable_text = f"{study.get('title', '')} {study.get('summary', '')} {study.get('dyscalculia_relevance', '')}".lower()
            
            if query in searchable_text:
                results.append({
                    'title': html.unescape(study.get('title', 'Unknown Title')),
                    'authors': study.get('authors', []),
                    'year': study.get('publication_year', 'Unknown'),
                    'relevance_score': study.get('relevance_score', 0),
                    'summary': html.unescape(study.get('summary', '')),
                    'dyscalculia_relevance': html.unescape(study.get('dyscalculia_relevance', '')),
                    'filename': study.get('filename', '')
                })
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return jsonify({
            'query': query,
            'results': results[:20],  # Limit to top 20 results
            'total_found': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/popular-queries', methods=['GET'])
def get_popular_queries():
    return jsonify({
        'queries': [
            'multiplication facts',
            'number sense',
            'math anxiety', 
            'visual strategies'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)