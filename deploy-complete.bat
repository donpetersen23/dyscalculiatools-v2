@echo off
echo ========================================
echo   Dyscalculia Tools - Complete Deploy
echo ========================================

REM Configuration - UPDATE THESE VALUES
set BUCKET_NAME=dyscalculia-tools-187249759
set DISTRIBUTION_ID=EMANNVI38BDCI

echo.
echo Configuration:
echo Bucket: %BUCKET_NAME%
echo Distribution: %DISTRIBUTION_ID%
echo.

if "%BUCKET_NAME%"=="your-bucket-name-here" (
    echo ERROR: Please update BUCKET_NAME in this script
    pause
    exit /b 1
)

if "%DISTRIBUTION_ID%"=="your-cloudfront-distribution-id-here" (
    echo ERROR: Please update DISTRIBUTION_ID in this script
    pause
    exit /b 1
)

echo Starting deployment...
echo.

REM Upload main HTML files
echo [1/6] Uploading HTML files...
aws s3 cp index.html s3://%BUCKET_NAME%/ --content-type "text/html" --cache-control "max-age=300"
aws s3 cp about.html s3://%BUCKET_NAME%/ --content-type "text/html" --cache-control "max-age=300"

REM Upload CSS
echo [2/6] Uploading CSS...
aws s3 cp styles.css s3://%BUCKET_NAME%/ --content-type "text/css" --cache-control "max-age=86400"

REM Upload JSON data files
echo [3/6] Uploading data files...
aws s3 cp tools_data.json s3://%BUCKET_NAME%/ --content-type "application/json" --cache-control "max-age=3600"
aws s3 cp research_metadata.json s3://%BUCKET_NAME%/ --content-type "application/json" --cache-control "max-age=3600"

REM Upload favicon files
echo [4/6] Uploading favicon files...
aws s3 cp favicon.ico s3://%BUCKET_NAME%/ --content-type "image/x-icon" --cache-control "max-age=2592000"
aws s3 cp favicon-32x32.png s3://%BUCKET_NAME%/ --content-type "image/png" --cache-control "max-age=2592000"
aws s3 cp apple-touch-icon.png s3://%BUCKET_NAME%/ --content-type "image/png" --cache-control "max-age=2592000"

REM Set bucket policy for public read access
echo [5/6] Ensuring public read access...
aws s3api put-bucket-policy --bucket %BUCKET_NAME% --policy file://bucket-policy.json

REM Invalidate CloudFront cache
echo [6/6] Invalidating CloudFront cache...
aws cloudfront create-invalidation --distribution-id %DISTRIBUTION_ID% --paths "/*"

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Your site should be live in a few minutes at your domain.
echo CloudFront cache invalidation may take 5-15 minutes to complete.
echo.
pause