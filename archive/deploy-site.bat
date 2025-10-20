@echo off
echo Deploying Dyscalculia Tools to S3...

REM Set your bucket name here (replace with your actual bucket name)
set BUCKET_NAME=your-bucket-name-here

REM Upload main files
echo Uploading HTML files...
aws s3 cp index.html s3://%BUCKET_NAME%/ --content-type "text/html"
aws s3 cp about.html s3://%BUCKET_NAME%/ --content-type "text/html"

REM Upload CSS
echo Uploading CSS...
aws s3 cp styles.css s3://%BUCKET_NAME%/ --content-type "text/css"

REM Upload JSON data files
echo Uploading data files...
aws s3 cp tools_data.json s3://%BUCKET_NAME%/ --content-type "application/json"
aws s3 cp research_metadata.json s3://%BUCKET_NAME%/ --content-type "application/json"

REM Upload favicon files
echo Uploading favicon files...
aws s3 cp favicon.ico s3://%BUCKET_NAME%/ --content-type "image/x-icon"
aws s3 cp favicon-32x32.png s3://%BUCKET_NAME%/ --content-type "image/png"
aws s3 cp apple-touch-icon.png s3://%BUCKET_NAME%/ --content-type "image/png"

echo Upload complete!
echo.
echo Next step: Invalidate CloudFront cache
echo Run: aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
echo.
pause