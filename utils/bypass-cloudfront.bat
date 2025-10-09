@echo off
echo Bypassing CloudFront and configuring direct S3 access...

REM Step 1: Enable static website hosting on S3 bucket
echo Step 1: Enabling static website hosting...
aws s3 website s3://dyscalculia-tools-187249759 --index-document index.html --error-document index.html

REM Step 2: Remove public access block
echo Step 2: Removing public access block...
aws s3api delete-public-access-block --bucket dyscalculia-tools-187249759

REM Step 3: Apply the updated bucket policy
echo Step 3: Applying public bucket policy...
aws s3api put-bucket-policy --bucket dyscalculia-tools-187249759 --policy file://bucket-policy.json

REM Step 4: Get the website endpoint for Route 53
echo Step 4: Getting S3 website endpoint...
aws s3api get-bucket-website --bucket dyscalculia-tools-187249759

echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo 1. Update your Route 53 hosted zone records:
echo    - Change A/AAAA records from CloudFront distribution
echo    - Point to S3 website endpoint: dyscalculia-tools-187249759.s3-website-us-east-1.amazonaws.com
echo.
echo 2. If using a custom domain, create CNAME record:
echo    - Name: your-domain.com
echo    - Value: dyscalculia-tools-187249759.s3-website-us-east-1.amazonaws.com
echo.
echo 3. Optional: Delete CloudFront distribution to save costs
echo    aws cloudfront delete-distribution --id EMANNVI38BDCI --if-match [ETag]
echo.
echo Configuration complete!