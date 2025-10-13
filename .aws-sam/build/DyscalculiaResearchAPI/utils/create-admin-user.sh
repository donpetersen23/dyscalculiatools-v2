#!/bin/bash

# Create IAM user for dyscalculia tools admin
aws iam create-user --user-name dyscalculia-admin

# Create and attach policy
aws iam put-user-policy --user-name dyscalculia-admin --policy-name DyscalculiaAdminPolicy --policy-document file://admin-policy.json

# Create access keys
aws iam create-access-key --user-name dyscalculia-admin