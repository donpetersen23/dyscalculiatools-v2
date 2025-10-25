# CodePipeline Setup Instructions

## Prerequisites
1. Your code must be in a GitHub repository
2. You need AWS CLI configured with admin access

## Step 1: Create GitHub Connection

1. Go to AWS Console → CodePipeline → Settings → Connections
2. Click "Create connection"
3. Choose "GitHub"
4. Name it: `dyscalculia-tools-github`
5. Click "Connect to GitHub" and authorize AWS
6. Copy the Connection ARN (looks like: `arn:aws:codestar-connections:us-east-1:123456789012:connection/abc-123`)

## Step 2: Deploy the Pipeline

```bash
aws cloudformation create-stack \
  --stack-name dyscalculia-tools-pipeline \
  --template-body file://pipeline.yaml \
  --parameters \
    ParameterKey=GitHubRepo,ParameterValue=YOUR_USERNAME/YOUR_REPO \
    ParameterKey=GitHubBranch,ParameterValue=main \
    ParameterKey=GitHubConnectionArn,ParameterValue=YOUR_CONNECTION_ARN \
  --capabilities CAPABILITY_IAM
```

Replace:
- `YOUR_USERNAME/YOUR_REPO` with your GitHub repo (e.g., `johndoe/dyscalculia-tools`)
- `YOUR_CONNECTION_ARN` with the ARN from Step 1

## Step 3: Wait for Pipeline Creation

```bash
aws cloudformation wait stack-create-complete --stack-name dyscalculia-tools-pipeline
```

## Step 4: View Your Pipeline

```bash
aws cloudformation describe-stacks \
  --stack-name dyscalculia-tools-pipeline \
  --query "Stacks[0].Outputs[?OutputKey=='PipelineUrl'].OutputValue" \
  --output text
```

Open the URL in your browser to see your pipeline!

## How It Works

1. **Push code to GitHub** → Pipeline automatically triggers
2. **Source stage** → Pulls code from GitHub
3. **Build stage** → Runs `sam build` and `sam package`
4. **Deploy stage** → Deploys to AWS via CloudFormation

## Testing the Pipeline

1. Make a change to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Test pipeline"
   git push
   ```
3. Watch the pipeline run in AWS Console

## Cost

- **CodePipeline:** $1/month (first pipeline free)
- **CodeBuild:** ~$0.01 per build (first 100 minutes/month free)
- **S3 artifacts:** < $0.10/month

**Total: ~$1-2/month**

## Removing GitHub Actions (Optional)

Once the pipeline is working, you can delete `.github/workflows/` from your repo since CodePipeline handles deployments now.

## Troubleshooting

**Pipeline fails at Source stage:**
- Check GitHub connection is active in AWS Console

**Pipeline fails at Build stage:**
- Check CodeBuild logs in AWS Console
- Verify `template.yaml` is in repo root

**Pipeline fails at Deploy stage:**
- Check CloudFormation events in AWS Console
- Verify IAM permissions are correct
