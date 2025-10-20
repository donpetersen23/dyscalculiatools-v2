@echo off
REM CloudFront/S3 deployment script

set S3_BUCKET=your-bucket-name

echo Uploading static files to S3...
aws s3 cp cloudfront/common.js s3://%S3_BUCKET%/common.js
aws s3 cp cloudfront/home.js s3://%S3_BUCKET%/home.js

echo Done! Files uploaded to S3.
pause
