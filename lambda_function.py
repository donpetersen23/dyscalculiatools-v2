import json
import boto3
import logging

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