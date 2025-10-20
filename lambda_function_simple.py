import json

def lambda_handler(event, context):
    """API handler - only handles /api/* endpoints"""
    
    path = event.get('rawPath', event.get('path', '/'))
    method = event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod', 'GET'))
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    # API: Search research
    if path == '/api/search' and method == 'POST':
        body = json.loads(event.get('body', '{}'))
        intervention = body.get('intervention', '')
        
        results = [{
            'title': f'Research on {intervention} for Dyscalculia',
            'authors': 'Sample Authors',
            'year': '2024',
            'summary': f'Study examining {intervention} interventions for dyscalculia.'
        }]
        
        headers['Content-Type'] = 'application/json'
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'intervention': intervention, 'results': results})
        }
    
    # API: Generate brief
    if path == '/api/generate-brief' and method == 'POST':
        body = json.loads(event.get('body', '{}'))
        intervention = body.get('intervention', '')
        
        headers['Content-Type'] = 'application/json'
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'brief': f'Evidence brief for {intervention} - coming soon.'})
        }
    
    # Unknown API endpoint
    headers['Content-Type'] = 'application/json'
    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({'error': 'API endpoint not found'})
    }