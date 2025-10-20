@echo off
REM Deployment script for Dyscalculia Tools

echo ====================================
echo Dyscalculia Tools Deployment Script
echo ====================================
echo.

REM Configuration - UPDATE THESE VALUES
set FUNCTION_NAME=dyscalculia-tools
set S3_BUCKET=your-bucket-name
set CDN_URL=https://your-cloudfront-domain.cloudfront.net
set AWS_REGION=us-east-1

echo Step 1: Creating Lambda deployment package...
cd lambda
powershell -Command "Compress-Archive -Path lambda_function.py -DestinationPath lambda.zip -Force"
echo Lambda package created.
echo.

echo Step 2: Deploying Lambda function...
aws lambda update-function-code --function-name %FUNCTION_NAME% --zip-file fileb://lambda.zip --region %AWS_REGION%
if %errorlevel% neq 0 (
    echo Lambda function not found. Creating new function...
    aws lambda create-function ^
        --function-name %FUNCTION_NAME% ^
        --runtime python3.9 ^
        --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role ^
        --handler lambda_function.lambda_handler ^
        --zip-file fileb://lambda.zip ^
        --timeout 10 ^
        --memory-size 256 ^
        --environment Variables={CDN_URL=%CDN_URL%} ^
        --region %AWS_REGION%
)
echo.

echo Step 3: Updating Lambda environment variables...
aws lambda update-function-configuration --function-name %FUNCTION_NAME% --environment Variables={CDN_URL=%CDN_URL%} --region %AWS_REGION%
echo.

cd ..

echo Step 4: Uploading static files to S3...
aws s3 cp cloudfront/common.js s3://%S3_BUCKET%/common.js
aws s3 cp cloudfront/home.js s3://%S3_BUCKET%/home.js
echo Static files uploaded.
echo.

echo ====================================
echo Deployment Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Configure API Gateway routes (/, /{proxy+})
echo 2. Test your endpoints
echo.
pause
