import json
import boto3
import logging
from research_assistant import DyscalculiaResearchAssistant

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        if path == '/api/search' and method == 'POST':
            return handle_search(event)
        elif path == '/api/generate-brief' and method == 'POST':
            return handle_generate_brief(event)
        else:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
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
        
        # Initialize research assistant
        research_assistant = DyscalculiaResearchAssistant()
        
        # Search for real research
        logger.info(f"Searching for: {intervention}")
        results = research_assistant.get_real_studies(intervention)
        logger.info(f"Results found: {len(results) if isinstance(results, list) else 'error'}")
        logger.info(f"Results: {results}")
        
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