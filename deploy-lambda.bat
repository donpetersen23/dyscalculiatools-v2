@echo off
REM Quick Lambda deployment script

set FUNCTION_NAME=dyscalculia-tools
set CDN_URL=https://your-cloudfront-domain.cloudfront.net
set AWS_REGION=us-east-1

echo Packaging Lambda function...
cd lambda
powershell -Command "Compress-Archive -Path lambda_function.py -DestinationPath lambda.zip -Force"

echo Deploying to AWS Lambda...
aws lambda update-function-code --function-name %FUNCTION_NAME% --zip-file fileb://lambda.zip --region %AWS_REGION%

echo Updating environment variables...
aws lambda update-function-configuration --function-name %FUNCTION_NAME% --environment Variables={CDN_URL=%CDN_URL%} --region %AWS_REGION%

cd ..
echo Done!
pause
