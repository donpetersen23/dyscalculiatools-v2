def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': '<h1>Test Lambda Works!</h1><p>Templates loading test...</p>'
    }