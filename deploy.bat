@echo off
echo Deploying CloudFront distribution...
aws cloudformation deploy ^
  --template-file cloudfront-distribution.yaml ^
  --stack-name dyscalculia-tools-cloudfront ^
  --capabilities CAPABILITY_IAM ^
  --region us-east-1

echo Getting distribution details...
aws cloudformation describe-stacks ^
  --stack-name dyscalculia-tools-cloudfront ^
  --region us-east-1 ^
  --query "Stacks[0].Outputs"