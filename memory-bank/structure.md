# File Structure

```
src/
├── app.py                    # Flask dev server
├── lambda/lambda_function.py # Production handler
├── templates/               # HTML components
├── tools_data.json         # Teaching tools
├── research_metadata.json  # Research data
├── template.yaml           # SAM config
├── styles.css             # Global styles
└── build.py               # Deployment prep
```

## Architecture
- **Dev**: Flask + file templates
- **Prod**: Lambda + API Gateway + S3 + CloudFront
- **Data**: JSON files (no database)
- **Templates**: Component-based with placeholders
- **Deploy**: SAM CLI + GitHub Actions
