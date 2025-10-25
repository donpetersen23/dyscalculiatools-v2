# Setting up dyscalculiatools.com Domain

## Prerequisites
- AWS CLI configured with appropriate permissions
- Route 53 hosted zone for dyscalculiatools.com already created
- SAM CLI installed

## Step-by-Step Setup

### 1. Create SSL Certificate
First, create an ACM certificate in **us-east-1** region (required for CloudFront):

```bash
aws acm request-certificate \
  --domain-name dyscalculiatools.com \
  --subject-alternative-names www.dyscalculiatools.com \
  --validation-method DNS \
  --region us-east-1
```

**Important**: Note the `CertificateArn` from the output.

### 2. Validate Certificate
- Go to AWS Console → Certificate Manager (us-east-1 region)
- Find your certificate and click "Create records in Route 53"
- This will automatically add the DNS validation records

### 3. Deploy Infrastructure
Run the deployment with your certificate ARN:

```bash
sam deploy --parameter-overrides CertificateArn=arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT-ID
```

### 4. Upload Website Files
Upload your static files to the S3 bucket:

```bash
aws s3 sync . s3://dyscalculiatools.com-website \
  --exclude "*.bat" \
  --exclude "*.py" \
  --exclude "*.yaml" \
  --exclude "*.toml" \
  --exclude "*.json" \
  --exclude ".git/*" \
  --exclude "lambda/*" \
  --exclude "templates/*" \
  --exclude "Research/*" \
  --exclude "clean-repo/*" \
  --exclude "docs/*" \
  --exclude ".github/*"
```

### 5. Get CloudFront Domain
Get the CloudFront distribution domain name:

```bash
aws cloudformation describe-stacks \
  --stack-name dyscalculia-tools-v2 \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomainName'].OutputValue" \
  --output text
```

### 6. Create Route 53 Records
Create DNS records pointing to CloudFront:

#### Option A: AWS Console
1. Go to Route 53 → Hosted zones → dyscalculiatools.com
2. Create two A records:
   - **Name**: `dyscalculiatools.com` → **Alias**: Yes → **Target**: CloudFront domain
   - **Name**: `www.dyscalculiatools.com` → **Alias**: Yes → **Target**: CloudFront domain

#### Option B: AWS CLI
```bash
# Get your hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name=='dyscalculiatools.com.'].Id" --output text)

# Create records (replace CF_DOMAIN with your CloudFront domain)
aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID --change-batch '{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "dyscalculiatools.com",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "CF_DOMAIN_HERE",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "Z2FDTNDATAQYW2"
        }
      }
    },
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "www.dyscalculiatools.com",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "CF_DOMAIN_HERE",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "Z2FDTNDATAQYW2"
        }
      }
    }
  ]
}'
```

## Architecture Overview

Your setup will include:
- **S3 Bucket**: Hosts static website files (HTML, CSS, JS)
- **CloudFront**: CDN with custom domain and SSL certificate
- **API Gateway + Lambda**: Handles dynamic API requests at `/api/*`
- **Route 53**: DNS records pointing to CloudFront

## URLs
- Main site: `https://dyscalculiatools.com`
- With www: `https://www.dyscalculiatools.com`
- API endpoints: `https://dyscalculiatools.com/api/*`

## Notes
- DNS propagation can take up to 48 hours
- SSL certificate must be in us-east-1 region for CloudFront
- Static files are served from S3 via CloudFront
- API calls are routed to Lambda functions