# Deployment Checklist

## Pre-Deployment Verification

- [x] Clean project structure (archive folder excluded from git)
- [x] GitHub Actions workflow configured with correct resources
- [x] Static assets in `/static` folder
- [x] Lambda function in `/lambda` folder
- [x] SAM templates validated

## Deployment Process

### Automatic Deployment (Recommended)

Every push to `main` branch triggers automatic deployment via GitHub Actions:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

**What happens:**
1. GitHub Actions workflow starts
2. SAM builds and deploys Lambda function
3. Static assets sync to S3 bucket: `dyscalculia-tools-536697250341`
4. CloudFront cache invalidated (Distribution: `E146D5Z1GVJDBX`)

### Manual Deployment (If Needed)

```bash
# Build and deploy Lambda
sam build
sam deploy

# Deploy static assets
aws s3 sync static/ s3://dyscalculia-tools-536697250341/ --cache-control "max-age=86400"

# Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id E146D5Z1GVJDBX --paths "/*"
```

## Post-Deployment Verification

1. **Check GitHub Actions**: https://github.com/donpetersen23/dyscalculiatools-v2/actions
2. **Test Live Site**: https://dyscalculiatools.com
3. **Verify CloudFront**: Check distribution E146D5Z1GVJDBX in AWS Console
4. **Check Lambda Logs**: CloudWatch logs for function errors

## Key Resources

- **S3 Bucket**: dyscalculia-tools-536697250341
- **CloudFront Distribution**: E146D5Z1GVJDBX
- **API Gateway**: lpbnig0i1g
- **Lambda Function**: dyscalculia-tools-v2-DyscalculiaResearchAPI-*
- **Stack Name**: dyscalculia-tools-v2

## Troubleshooting

### Static Assets Not Loading
- Verify S3 sync completed successfully
- Check CloudFront invalidation status
- Confirm OAC permissions in S3 bucket policy

### Lambda Errors
- Check CloudWatch logs
- Verify environment variables (CDN_URL, S3_BUCKET)
- Test locally with `sam local start-api`

### 403 Errors
- See `docs/403-fix-tracking.md` for historical fixes
- Verify CloudFront OAC configuration
- Check S3 bucket policy allows CloudFront access
