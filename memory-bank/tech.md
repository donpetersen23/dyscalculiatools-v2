# Tech Stack

## Languages
- Python 3.11 (Flask, boto3, psutil)
- HTML5, CSS3, JavaScript ES6+

## AWS Services
- Lambda, API Gateway, S3, CloudFront, SAM

## Commands
```bash
# Local dev
python app.py

# Deploy
sam build && sam deploy
```

## Config
- Stack: dyscalculia-tools-v2
- Region: us-east-1
- Domain: dyscalculiatools.com
- Lambda: 512MB, 30s timeout
