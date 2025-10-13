import json
import boto3

def test_bedrock_api():
    """Test the correct Bedrock API format"""
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    prompt = "Extract the title from this text: 'Research on Math Learning'"
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": prompt
            }]
        }]
    }
    
    try:
        response = bedrock.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 100,
                    "temperature": 0.1
                }
            })
        )
        
        result = json.loads(response['body'].read())
        content = result['results'][0]['outputText']
        print(f"Success: {content}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_bedrock_api()