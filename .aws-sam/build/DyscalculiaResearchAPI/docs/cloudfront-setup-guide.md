# CloudFront Setup Guide for Dyscalculia Tools

## Step 1: Create CloudFront Distribution

1. Go to AWS CloudFront console
2. Click "Create Distribution"
3. Configure:
   - **Origin Domain**: dyscalculia-tools-187249759.s3.amazonaws.com
   - **Origin Access**: Origin Access Control (OAC)
   - **Create new OAC**: Yes
   - **Default Root Object**: index.html (if applicable)

## Step 2: Update S3 Bucket Policy

After creating the distribution, update the bucket policy with the actual distribution ARN:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::dyscalculia-tools-187249759/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

## Step 3: Test Access

- Test CloudFront URL: `https://YOUR_DISTRIBUTION_DOMAIN.cloudfront.net`
- Verify S3 direct access is blocked

## Benefits

- **Security**: S3 bucket is private
- **Performance**: Global CDN caching
- **Cost**: Reduced S3 data transfer costs
- **SSL**: Free SSL certificate included