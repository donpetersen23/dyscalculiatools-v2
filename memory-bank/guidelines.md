# Quick Reference

## Essential Patterns
- UTF-8 encoding: `open('file.json', 'r', encoding='utf-8')`
- Safe dict access: `tool.get('title', '')`
- Template placeholders: `{{title}}`, `{{content}}`
- Error handling: Return `[]` on FileNotFoundError
- F-strings: `f'<li>{step}</li>'`
- List comprehensions: `''.join([f'<span>{tag}</span>' for tag in tags])`

## Flask vs Lambda
**Flask**: File templates, `send_from_directory()`, port 5000
**Lambda**: In-memory templates, CDN URLs, API Gateway proxy

## Common Code Blocks
```python
# Data loading
def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Template assembly  
html = base.replace('{{title}}', title)
html = html.replace('{{content}}', content)

# Lambda handler
def lambda_handler(event, context):
    path = event.get('rawPath', event.get('path', '/'))
    return {'statusCode': 200, 'body': html}
```
