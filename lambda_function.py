import json
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Load tools data
try:
    with open('tools_data.json', 'r') as f:
        TOOLS_DATA = json.load(f)
except FileNotFoundError:
    logger.error("tools_data.json not found")
    TOOLS_DATA = []

def lambda_handler(event, context):
    """AWS Lambda handler for the research assistant API"""
    
    # Handle CORS preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    try:
        # Parse the request
        path = event.get('path', '')
        method = event.get('httpMethod', 'GET')
        
        # Handle API routes
        if path == '/' and method == 'GET':
            return handle_homepage(event)
        elif path == '/about' and method == 'GET':
            return handle_about_page(event)
        elif path == '/api/search' and method == 'POST':
            return handle_search(event)
        elif path == '/api/generate-brief' and method == 'POST':
            return handle_generate_brief(event)
        elif path.startswith('/tool/') and method == 'GET':
            return handle_tool_page(event)
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>404 - Page Not Found</h1>'
            }
            
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error</h1><p>{str(e)}</p>'
        }

def handle_search(event):
    """Handle research search requests"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        intervention = body.get('intervention', '')
        
        if not intervention:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'No intervention specified'})
            }
        
        # Return mock results for now
        logger.info(f"Searching for: {intervention}")
        results = [
            {
                'title': f'Research on {intervention} for Dyscalculia',
                'authors': 'Sample Authors',
                'year': '2024',
                'summary': f'This study examines the effectiveness of {intervention} interventions for students with dyscalculia.'
            }
        ]
        logger.info(f"Results found: {len(results)}")
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'intervention': intervention,
                'results': results
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def handle_generate_brief(event):
    """Handle brief generation requests"""
    try:
        body = json.loads(event.get('body', '{}'))
        intervention = body.get('intervention', '')
        studies = body.get('studies', [])
        
        brief = f"Evidence brief for {intervention} - functionality coming soon."
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'brief': brief})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }

def handle_tool_page(event):
    """Generate complete HTML page for a specific tool"""
    try:
        # Extract tool ID from path (e.g., /tool/multiplication-grid)
        path = event.get('path', '')
        tool_id = path.replace('/tool/', '')
        
        # Find the tool in data
        tool = None
        for t in TOOLS_DATA:
            if t.get('id') == tool_id:
                tool = t
                break
        
        if not tool:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '<h1>Tool not found</h1>'
            }
        
        # Load templates
        with open('templates/base.html', 'r') as f:
            base_template = f.read()
        with open('templates/tool_detail.html', 'r') as f:
            tool_template = f.read()
        
        # Build steps HTML
        steps_html = ''.join([f'<li>{step}</li>' for step in tool.get('steps', [])])
        
        # Build challenges HTML
        challenges_html = '<ul>' + ''.join([f'<li>{c}</li>' for c in tool.get('challenges', [])]) + '</ul>'
        
        # Build tags HTML
        tags_html = ''.join([f'<span class="tag tool-tag">{tag}</span>' for tag in tool.get('tags', [])])
        
        # Fill in tool template
        tool_content = tool_template.replace('{{title}}', tool.get('title', ''))
        tool_content = tool_content.replace('{{description}}', tool.get('description', ''))
        tool_content = tool_content.replace('{{age_range}}', tool.get('age_range', ''))
        tool_content = tool_content.replace('{{setting}}', tool.get('setting', ''))
        tool_content = tool_content.replace('{{time_required}}', tool.get('time_required', ''))
        tool_content = tool_content.replace('{{materials}}', tool.get('materials', ''))
        tool_content = tool_content.replace('{{steps}}', steps_html)
        tool_content = tool_content.replace('{{challenges}}', challenges_html)
        tool_content = tool_content.replace('{{tags}}', tags_html)
        
        # Fill in base template
        html = base_template.replace('{{title}}', tool.get('title', ''))
        html = html.replace('{{content}}', tool_content)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html
        }
        
    except Exception as e:
        logger.error(f"Error generating tool page: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error</h1><p>{str(e)}</p>'
        }

def handle_homepage(event):
    """Generate homepage from components"""
    try:
        with open('templates/base.html', 'r') as f:
            base = f.read()
        with open('templates/home-content.html', 'r') as f:
            content = f.read()
        with open('templates/home-scripts.html', 'r') as f:
            scripts = f.read()
        
        html = base.replace('{{title}}', 'Home')
        html = html.replace('{{content}}', content)
        html = html.replace('{{scripts}}', scripts)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html
        }
        
    except Exception as e:
        logger.error(f"Error generating homepage: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error</h1><p>{str(e)}</p>'
        }

def handle_about_page(event):
    """Generate about page from components"""
    try:
        with open('templates/base.html', 'r') as f:
            base = f.read()
        with open('templates/about-content.html', 'r') as f:
            content = f.read()
        with open('templates/about-scripts.html', 'r') as f:
            scripts = f.read()
        
        html = base.replace('{{title}}', 'About')
        html = html.replace('{{content}}', content)
        html = html.replace('{{scripts}}', scripts)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html
        }
        
    except Exception as e:
        logger.error(f"Error generating about page: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error</h1><p>{str(e)}</p>'
        }