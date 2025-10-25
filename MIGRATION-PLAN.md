# Migration to Hybrid Static + API Architecture

## 🎯 Goal
Convert from Lambda-rendered pages to static HTML + Lambda APIs for better performance and lower costs.

## 📋 Phase-by-Phase Plan

### ✅ PHASE 1: Build Static Pages (SAFE - No Live Changes)
**Status:** Ready to execute
**Risk:** ZERO - Nothing deployed yet

**Steps:**
1. Run build script locally:
   ```bash
   python build_static_pages.py
   ```

2. Verify output:
   ```bash
   python test_static_build.py
   ```

3. Check generated files:
   ```bash
   dir static\*.html
   ```

4. Open files in browser to verify they look correct

5. Commit to git (but don't push yet):
   ```bash
   git add build_static_pages.py test_static_build.py MIGRATION-PLAN.md
   git commit -m "Add static page generation (Phase 1 - not deployed)"
   ```

**Success Criteria:**
- ✓ index.html, about.html, contact.html exist in static/
- ✓ All tests pass
- ✓ Pages look correct in browser
- ✓ Live site unchanged

---

### ✅ PHASE 2: Deploy Static Files (LOW RISK - Parallel System)
**Status:** After Phase 1 complete
**Risk:** VERY LOW - Lambda still serving pages

**Steps:**
1. Update pipeline to build static pages:
   - Add build step to pipeline.yaml or .github/workflows/deploy.yml
   - Run `python build_static_pages.py` before SAM deploy

2. Push changes:
   ```bash
   git push origin main
   ```

3. Wait for pipeline to complete

4. Verify static files uploaded to S3:
   ```bash
   aws s3 ls s3://dyscalculia-tools-536697250341/ --region us-east-1
   ```

5. Test S3 URLs directly (bypass CloudFront):
   ```bash
   curl https://dyscalculia-tools-536697250341.s3.amazonaws.com/index.html
   ```

**Success Criteria:**
- ✓ Pipeline succeeds
- ✓ Static HTML files in S3
- ✓ S3 URLs return correct HTML
- ✓ Live site still works (using Lambda)

**Rollback:** Not needed - Lambda still serving live site

---

### ⚠️ PHASE 3: Switch CloudFront to Static (MEDIUM RISK - Changes Live Site)
**Status:** After Phase 2 complete
**Risk:** MEDIUM - Changes what users see

**Steps:**
1. Test one page first - Update CloudFront to serve /about from S3:
   - Modify template.yaml CloudFront DefaultCacheBehavior
   - Change TargetOriginId from APIOrigin to S3Origin
   - Add DefaultRootObject: index.html

2. Deploy CloudFront change

3. Test /about page:
   ```bash
   curl https://dyscalculiatools.com/about
   ```

4. If good, update CloudFront for all pages

5. Test live site thoroughly:
   - Visit https://dyscalculiatools.com/
   - Click all links
   - Test search functionality
   - Check mobile view

**Success Criteria:**
- ✓ Pages load fast (<100ms)
- ✓ All links work
- ✓ CSS/JS load correctly
- ✓ Search still works

**Rollback Plan:**
```bash
# Revert CloudFront to use Lambda
aws cloudformation update-stack --stack-name dyscalculia-tools-v2 \
  --use-previous-template --region us-east-1
# Takes ~5 minutes
```

---

### ✅ PHASE 4: Clean Up Lambda (SAFE - Optimization)
**Status:** After Phase 3 verified working
**Risk:** LOW - Static pages already working

**Steps:**
1. Update lambda/lambda_function.py:
   - Remove COMPONENTS dict
   - Remove PAGES dict
   - Keep only API handlers

2. Update template.yaml:
   - Remove Lambda events for /, /about, /contact
   - Keep only /api/* events

3. Deploy

4. Verify APIs still work:
   ```bash
   curl https://dyscalculiatools.com/api/health
   ```

**Success Criteria:**
- ✓ Lambda package smaller
- ✓ APIs still work
- ✓ Static pages unchanged

**Rollback:** Redeploy previous Lambda version

---

## 📊 Expected Results

### Performance:
- **Before:** 100-300ms page load
- **After:** 10-50ms page load

### Cost (per 10K requests):
- **Before:** $0.17
- **After:** $0.01

### Lambda Package:
- **Before:** 3 KB
- **After:** 2 KB (API only)

---

## 🚨 Emergency Rollback (Any Phase)

If anything breaks:
```bash
# Option 1: Revert last commit
git revert HEAD
git push origin main

# Option 2: Redeploy previous version
git reset --hard HEAD~1
git push --force origin main

# Option 3: Manual CloudFront fix
# Update CloudFront to point back to Lambda
```

---

## ✅ Current Status: PHASE 1 READY

**Next Action:** Run `python build_static_pages.py` locally to test
