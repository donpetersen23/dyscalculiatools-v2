#!/usr/bin/env python3
import json
import boto3
import sys

def validate_aws_resources():
    """Validate that AWS resources in config actually exist"""
    with open('aws-config.json') as f:
        config = json.load(f)
    
    aws_config = config['aws']
    s3_bucket = aws_config['s3_bucket']
    distribution_id = aws_config['cloudfront_distribution_id']
    
    # Check S3 bucket
    s3 = boto3.client('s3')
    try:
        s3.head_bucket(Bucket=s3_bucket)
        print(f"✓ S3 bucket {s3_bucket} exists")
    except Exception as e:
        print(f"✗ S3 bucket {s3_bucket} not found: {e}")
        return False
    
    # Check CloudFront distribution
    cf = boto3.client('cloudfront')
    try:
        cf.get_distribution(Id=distribution_id)
        print(f"✓ CloudFront distribution {distribution_id} exists")
    except Exception as e:
        print(f"✗ CloudFront distribution {distribution_id} not found: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if not validate_aws_resources():
        sys.exit(1)
    print("All AWS resources validated successfully")