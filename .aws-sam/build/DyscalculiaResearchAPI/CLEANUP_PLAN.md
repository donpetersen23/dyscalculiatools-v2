# Dyscalculia Tools Cleanup Plan

## Files to Remove (Safe to Delete)

### Duplicate/Temporary Configuration Files
- bucket-policy-private-for-cloudfront.json
- bucket-policy-referer-restricted.json  
- bucket-policy-with-deny.json
- cloudfront-alias-dns.json
- cloudfront-config.json
- cloudfront-dns-records.json
- current-config.json (corrupted file)
- delete-www-cname.json
- distribution-config.json (corrupted file)
- dns-change.json
- dns-records.json
- root-alias-dns.json
- root-dns.json
- ssl-validation-records.json
- tools-dns.json
- update-cloudfront.json
- update-distribution.json
- updated-distribution-config.json

### Test Files
- test_assistant.py
- test_research_live.py
- setup_research_assistant.py

### Research PDFs (Move to S3 or separate storage)
- All PDF files in root directory (10+ files)

### Redundant Files
- app.py (if using Lambda) OR lambda_function.py (if using Flask)

## Files to Keep
- index.html
- research.html
- styles.css
- research_assistant.py
- requirements.txt
- template.yaml (for Lambda)
- cloudformation.yml (for infrastructure)
- bucket-policy.json (main policy)
- admin-policy.json
- samconfig.toml
- deploy.bat
- .github/workflows/deploy.yml

## Estimated Space Savings
- Configuration files: ~500KB
- PDF files: ~50MB
- Test files: ~50KB
- Total: ~50MB+ reduction

## Performance Improvements
1. Faster deployments (fewer files to upload)
2. Cleaner project structure
3. Reduced CloudFormation template complexity
4. Better maintainability