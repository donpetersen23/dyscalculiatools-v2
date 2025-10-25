# Dyscalculia Tools

A serverless web application providing research-based tools and resources for dyscalculia support.

## Architecture

**Hybrid Static + API Model** for optimal performance and cost:

- **Static Pages**: HTML served from S3 via CloudFront (homepage, about, contact)
- **API Endpoints**: AWS Lambda (Python 3.11) with HTTP API Gateway (`/api/*`)
- **Storage**: S3 for static assets (CSS, JS, images, JSON)
- **CDN**: CloudFront with custom domain (dyscalculiatools.com)
- **CI/CD**: GitHub Actions with automated deployments

### Request Flow
```
User Request → CloudFront
    ├─→ S3 (*.html, *.css, *.js, *.json, images) - Cached, fast
    └─→ Lambda (/api/*) - Dynamic API responses
```

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
├── lambda/                    # Lambda function code (API only)
│   └── lambda_function.py
├── templates/                 # HTML templates (source)
├── static/                    # Generated HTML + static assets
│   ├── index.html            # Generated from templates
│   ├── about.html            # Generated from templates
│   ├── contact.html          # Generated from templates
│   ├── styles.css
│   ├── *.js
│   └── *.json
├── docs/                      # Documentation
├── build_static_pages.py      # Build script (generates HTML)
├── test_static_build.py       # Validates generated HTML
├── template.yaml              # Infrastructure definition
├── aws-config.json            # AWS resource configuration
└── README.md
```

## Local Development

### Prerequisites
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.11

### Build Static Pages

```bash
# Generate static HTML from templates
python build_static_pages.py

# Validate generated HTML
python test_static_build.py

# Preview in browser
start static/index.html
```

### Testing Lambda (API)

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

The project uses GitHub Actions for automated deployments:

1. **Build Static Pages**: Generates HTML from templates
2. **Deploy Lambda**: Builds and deploys API function via SAM
3. **Upload to S3**: Syncs static files to S3 bucket
4. **Invalidate CloudFront**: Clears CDN cache

### Deployment Steps
```bash
python build_static_pages.py              # Generate HTML
sam build && sam deploy                    # Deploy Lambda
aws s3 sync static/ s3://bucket/          # Upload static files
aws cloudfront create-invalidation ...     # Clear cache
```

## Deployment

Every push to `main` branch automatically triggers GitHub Actions:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Monitor deployment: https://github.com/donpetersen23/dyscalculiatools-v2/actions

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
