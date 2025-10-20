@echo off
echo ========================================
echo Building and Deploying Dyscalculia Tools
echo ========================================

echo.
echo [1/4] Building HTML files from components...
python build.py
if errorlevel 1 (
    echo ERROR: Build failed
    exit /b 1
)

echo.
echo [2/4] Deploying Lambda function...
call sam build
call sam deploy --no-confirm-changeset
if errorlevel 1 (
    echo ERROR: Lambda deployment failed
    exit /b 1
)

echo.
echo [3/4] Uploading static files to S3...
aws s3 sync . s3://dyscalculiatools.com-website ^
    --exclude "*" ^
    --include "index.html" ^
    --include "about.html" ^
    --include "styles.css" ^
    --include "*.json" ^
    --include "*.png" ^
    --include "*.ico" ^
    --cache-control "max-age=300"

echo.
echo [4/4] Invalidating CloudFront cache...
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name dyscalculiatools --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" --output text') do set DIST_ID=%%i
aws cloudfront create-invalidation --distribution-id %DIST_ID% --paths "/*"

echo.
echo ========================================
echo ✅ Deployment Complete!
echo ========================================
echo.
echo Your site is live at: https://dyscalculiatools.com
