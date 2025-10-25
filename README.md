# Dyscalculia Tools

A serverless web application providing research-based tools and resources for dyscalculia support.

## Architecture

- **Frontend**: Static HTML/CSS/JS served via CloudFront
- **Backend**: AWS Lambda (Python 3.11) with HTTP API Gateway
- **Storage**: S3 for static assets
- **CDN**: CloudFront with custom domain (dyscalculiatools.com)
- **CI/CD**: AWS CodePipeline with automated deployments from GitHub

## Infrastructure

All infrastructure is defined as code using AWS SAM (Serverless Application Model):

- `template.yaml` - Main infrastructure definition
- `pipeline.yaml` - CI/CD pipeline definition

### Key Resources

- **CloudFront Distribution**: E146D5Z1GVJDBX
- **HTTP API Gateway**: lpbnig0i1g
- **S3 Bucket**: dyscalculia-tools-536697250341
- **Lambda Function**: dyscalculia-tools-v2-DyscalculiaResearchAPI-*

## Project Structure

```
dyscalculiatools/
├── lambda/                 # Lambda function code
│   └── lambda_function.py
├── templates/              # HTML templates
├── static/                 # CSS, JS, images, JSON data
├── docs/                   # Documentation
├── template.yaml          # Infrastructure definition
├── pipeline.yaml          # CI/CD pipeline
├── requirements.txt       # Python dependencies
├── aws-config.json        # AWS resource configuration
└── README.md
```

## Local Development

### Prerequisites
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.11

### Testing Locally

```bash
# Validate template
sam validate

# Test Lambda locally
sam local start-api

# Test specific function
sam local invoke DyscalculiaResearchAPI --event test-payload.json
```

### Manual Deployment (Optional)

```bash
sam build
sam deploy
```

**Note**: Production deployments happen automatically via CodePipeline when pushing to the `main` branch.

## CI/CD Pipeline

The project uses AWS CodePipeline for automated deployments:

1. **Source**: Pulls from `donpetersen23/dyscalculiatools-v2` (main branch)
2. **Build**: Runs `sam build` and `sam package` via CodeBuild
3. **Deploy**: Deploys to CloudFormation stack `dyscalculia-tools-v2`

### Pipeline Details
- **Pipeline**: dyscalculia-pipeline-pipeline
- **GitHub Connection**: arn:aws:codeconnections:us-east-1:536697250341:connection/065a759a-dfa6-4689-8dbe-35ad168a8521

## Deployment

Every push to `main` branch automatically triggers the pipeline:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Monitor deployment: https://console.aws.amazon.com/codesuite/codepipeline/pipelines/dyscalculia-pipeline-pipeline/view

## Monitoring

CloudWatch Alarms are configured for:
- Lambda function errors (threshold: 5 errors in 5 minutes)
- API Gateway 5xx errors (threshold: 10 errors in 5 minutes)

## Documentation

See `docs/` folder for detailed documentation:
- `PIPELINE-SETUP.md` - CI/CD setup instructions
- `403-fix-tracking.md` - Historical troubleshooting log
- Additional guides and architecture docs

## Live Site

https://dyscalculiatools.com

## License

[Your License Here]
