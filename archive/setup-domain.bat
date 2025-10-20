@echo off
echo Setting up dyscalculiatools.com domain...

REM Step 1: Create ACM certificate (must be in us-east-1 for CloudFront)
echo.
echo Step 1: Creating SSL certificate...
echo You need to create an ACM certificate in us-east-1 region first.
echo Run this command in AWS CLI:
echo.
echo aws acm request-certificate --domain-name dyscalculiatools.com --subject-alternative-names www.dyscalculiatools.com --validation-method DNS --region us-east-1
echo.
echo After running the command, note the CertificateArn from the output.
echo Then validate the certificate by adding the DNS records to Route 53.
echo.
pause

REM Step 2: Deploy the stack with certificate ARN
set /p CERT_ARN="Enter the Certificate ARN from Step 1: "

echo.
echo Step 2: Deploying infrastructure...
sam deploy --parameter-overrides CertificateArn=%CERT_ARN%

if %ERRORLEVEL% neq 0 (
    echo Deployment failed!
    pause
    exit /b 1
)

REM Step 3: Upload website files to S3
echo.
echo Step 3: Uploading website files...
aws s3 sync . s3://dyscalculiatools.com-website --exclude "*.bat" --exclude "*.py" --exclude "*.yaml" --exclude "*.toml" --exclude "*.json" --exclude ".git/*" --exclude "lambda/*" --exclude "templates/*" --exclude "Research/*" --exclude "clean-repo/*" --exclude "docs/*" --exclude ".github/*"

REM Step 4: Get CloudFront distribution domain
echo.
echo Step 4: Getting CloudFront information...
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name dyscalculia-tools-v2 --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomainName'].OutputValue" --output text') do set CF_DOMAIN=%%i

echo.
echo CloudFront Domain: %CF_DOMAIN%
echo.
echo Step 5: Create Route 53 records
echo You need to create these DNS records in Route 53:
echo.
echo Record 1:
echo   Name: dyscalculiatools.com
echo   Type: A
echo   Alias: Yes
echo   Target: %CF_DOMAIN%
echo.
echo Record 2:
echo   Name: www.dyscalculiatools.com
echo   Type: A
echo   Alias: Yes
echo   Target: %CF_DOMAIN%
echo.
echo Or run these AWS CLI commands:
echo.

REM Get the hosted zone ID
for /f "tokens=*" %%i in ('aws route53 list-hosted-zones --query "HostedZones[?Name=='dyscalculiatools.com.'].Id" --output text') do set ZONE_ID=%%i

if "%ZONE_ID%"=="" (
    echo No hosted zone found for dyscalculiatools.com
    echo Please create a hosted zone first or check the domain name.
) else (
    echo aws route53 change-resource-record-sets --hosted-zone-id %ZONE_ID% --change-batch file://route53-records.json
    
    REM Create the Route 53 change batch file
    echo Creating Route 53 records file...
    (
        echo {
        echo   "Changes": [
        echo     {
        echo       "Action": "UPSERT",
        echo       "ResourceRecordSet": {
        echo         "Name": "dyscalculiatools.com",
        echo         "Type": "A",
        echo         "AliasTarget": {
        echo           "DNSName": "%CF_DOMAIN%",
        echo           "EvaluateTargetHealth": false,
        echo           "HostedZoneId": "Z2FDTNDATAQYW2"
        echo         }
        echo       }
        echo     },
        echo     {
        echo       "Action": "UPSERT",
        echo       "ResourceRecordSet": {
        echo         "Name": "www.dyscalculiatools.com",
        echo         "Type": "A",
        echo         "AliasTarget": {
        echo           "DNSName": "%CF_DOMAIN%",
        echo           "EvaluateTargetHealth": false,
        echo           "HostedZoneId": "Z2FDTNDATAQYW2"
        echo         }
        echo       }
        echo     }
        echo   ]
        echo }
    ) > route53-records.json
    
    echo.
    echo Applying Route 53 records...
    aws route53 change-resource-record-sets --hosted-zone-id %ZONE_ID% --change-batch file://route53-records.json
    
    if %ERRORLEVEL% equ 0 (
        echo.
        echo ✅ Domain setup complete!
        echo Your website will be available at https://dyscalculiatools.com
        echo Note: DNS propagation may take up to 48 hours.
    ) else (
        echo ❌ Failed to create Route 53 records.
    )
)

echo.
echo Setup complete! Your website should be available at:
echo https://dyscalculiatools.com
echo https://www.dyscalculiatools.com
echo.
pause