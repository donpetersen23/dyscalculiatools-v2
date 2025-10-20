@echo off
REM Complete infrastructure setup script

set FUNCTION_NAME=dyscalculia-tools
set API_NAME=dyscalculia-api
set AWS_REGION=us-east-1
set ACCOUNT_ID=YOUR_ACCOUNT_ID

echo ====================================
echo Infrastructure Setup
echo ====================================
echo.

echo Step 1: Creating IAM role for Lambda...
aws iam create-role ^
    --role-name lambda-dyscalculia-role ^
    --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"

aws iam attach-role-policy ^
    --role-name lambda-dyscalculia-role ^
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

echo Waiting 10 seconds for IAM role to propagate...
timeout /t 10 /nobreak
echo.

echo Step 2: Creating Lambda function...
cd lambda
powershell -Command "Compress-Archive -Path lambda_function.py -DestinationPath lambda.zip -Force"

aws lambda create-function ^
    --function-name %FUNCTION_NAME% ^
    --runtime python3.9 ^
    --role arn:aws:iam::%ACCOUNT_ID%:role/lambda-dyscalculia-role ^
    --handler lambda_function.lambda_handler ^
    --zip-file fileb://lambda.zip ^
    --timeout 10 ^
    --memory-size 256 ^
    --region %AWS_REGION%

cd ..
echo.

echo Step 3: Creating HTTP API Gateway...
aws apigatewayv2 create-api ^
    --name %API_NAME% ^
    --protocol-type HTTP ^
    --target arn:aws:lambda:%AWS_REGION%:%ACCOUNT_ID%:function:%FUNCTION_NAME% ^
    --region %AWS_REGION%

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo IMPORTANT: Update these values in deploy.bat:
echo - ACCOUNT_ID
echo - S3_BUCKET
echo - CDN_URL
echo.
echo Then run deploy.bat to deploy your code.
echo.
pause
