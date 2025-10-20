# Lambda Deployment Guide

## Setup Instructions

### 1. Deploy Lambda Function
- Upload `lambda_function.py` to AWS Lambda
- Set runtime to Python 3.9 or higher
- Set handler to `lambda_function.lambda_handler`

### 2. Configure Environment Variable
Add environment variable in Lambda:
- Key: `CDN_URL`
- Value: `https://your-cloudfront-domain.cloudfront.net` (replace with your actual CloudFront URL)

### 3. Configure API Gateway
Create HTTP API or REST API with:
- Route: `/{proxy+}` (catch-all for all paths)
- Route: `/` (root path)
- Integration: Lambda proxy integration
- Enable CORS if needed

### 4. Upload to CloudFront
Upload these files from the `cloudfront/` folder:
- `common.js`
- `home.js`
- `styles.css` (your existing file)
- `tools_data.json` (your existing file)
- `research_metadata.json` (your existing file)
- All favicon files

### 5. Test Routes
- `/` - Home page with tools and research
- `/about` - About page
- `/contact` - Contact page

## Architecture Benefits
- **Fast**: Static assets served from CloudFront edge locations
- **Scalable**: Lambda auto-scales with traffic
- **Maintainable**: Shared header/footer in one place
- **Cost-effective**: Pay only for Lambda invocations and CloudFront bandwidth
