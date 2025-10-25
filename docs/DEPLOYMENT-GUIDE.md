# Dyscalculia Tools - Deployment Guide

## Quick Deploy Steps

### 1. Update Configuration
Edit `deploy-complete.bat` and update these values:
- `BUCKET_NAME`: Your S3 bucket name (looks like it's `dyscalculia-tools-187249759`)
- `DISTRIBUTION_ID`: Your CloudFront distribution ID (looks like it's `EMANNVI38BDCI`)

### 2. Run Deployment
```bash
deploy-complete.bat
```

This will:
- Upload all your site files to S3
- Set proper content types and cache headers
- Invalidate CloudFront cache
- Make your site live

### 3. Verify Deployment
- Check your domain in a browser
- Verify all functionality works
- Test the search features

## Files Being Deployed
- `index.html` - Main homepage
- `about.html` - About page
- `styles.css` - All styling
- `tools_data.json` - Tools database
- `research_metadata.json` - Research database
- Favicon files

## Cache Settings
- HTML files: 5 minutes (for quick updates)
- CSS files: 24 hours
- JSON data: 1 hour
- Images: 30 days

## Troubleshooting
- If changes don't appear, wait 5-15 minutes for CloudFront cache invalidation
- Check AWS CLI is configured: `aws configure list`
- Verify bucket permissions if upload fails

## Manual Commands (if needed)
```bash
# Upload single file
aws s3 cp index.html s3://your-bucket-name/

# Invalidate cache manually
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```