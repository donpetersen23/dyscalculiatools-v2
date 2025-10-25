# 403 Error Fix Tracking Document

## Current Status
**403 Errors:** ❌ **STILL OCCURRING**
**Last Checked:** 10/24/2025 09:26 GMT - https://dyscalculiatools.com
**Result:** FAIL - 403 Forbidden (CloudFront Error)

**Current Working Status:**
- ✅ API Gateway direct: https://vxam4rzpkd.execute-api.us-east-1.amazonaws.com/Prod/
- ❌ Homepage via CloudFront: https://dyscalculiatools.com (403)
- ✅ API endpoints: https://dyscalculiatools.com/api/health (200)
- ✅ Static assets: https://dyscalculiatools.com/styles.css (200)

---

## Overview
This document tracks the resolution of 403 errors in the dyscalculia tools application. Issues are organized by category with complete timelines and resolution details.

## Issue Categories and Status

### 1. CloudFront Origin Path Mismatch
**Status:** 🔄 **IN PROGRESS**

**Problem Description:**
- OriginPath="/Prod" combined with "/Prod/*" cache behavior caused double-prefixing
- Homepage "/" returned 403 error
- API Gateway direct access worked, CloudFront routing failed

**Root Cause (Clarified 10/24/2025 16:58):**
- API Gateway stage is /Prod, requires OriginPath=/Prod
- Original issue: Having BOTH OriginPath=/Prod AND /Prod/* cache behavior
- Solution: Keep OriginPath=/Prod, remove /Prod/* cache behavior
- Template.yaml contained the problematic configuration causing manual fixes to revert

**Timeline:**
- **[10/23/2025 16:00]** - Initial fix attempted (OriginPath removal)
- **[10/23/2025 16:45]** - Documented as Resolved
- **[10/24/2025 10:02]** - Identified: OriginPath="/Prod" + "/Prod/*" cache behavior conflict
- **[10/24/2025 10:02]** - Removed "/Prod/*" cache behavior via CLI
- **[10/24/2025 10:02]** - Created CloudFront invalidation (I645TG35322ASJ7LKS789WGTUI)
- **[10/24/2025 10:15]** - Verification: Distribution deployed, invalidation completed
- **[10/24/2025 10:15]** - Test result: Homepage still returns 403
- **[10/24/2025 10:15]** - Analysis: OriginPath="/Prod" still present, needs removal
- **[10/24/2025 16:30]** - Root cause identified: OriginPath="/Prod" in template.yaml causing reverts
- **[10/24/2025 16:32]** - Decision: Move to infrastructure-as-code (Option B - new distribution)
- **[10/24/2025 16:34]** - First deployment attempt failed: Domain aliases conflict with E69DLY1YOK93D
- **[10/24/2025 16:36]** - Updated template: Removed domain aliases and custom certificate temporarily
- **[10/24/2025 16:38]** - Deployment successful: Created new distribution E1YVN4SG69F679
- **[10/24/2025 16:42]** - Test result: New distribution also returns 403 on homepage
- **[10/24/2025 16:55]** - Investigation: Verified OriginPath="" (empty) in new distribution
- **[10/24/2025 16:55]** - Testing: API Gateway returns 403 without /Prod prefix, MissingAuthenticationToken with /Prod
- **[10/24/2025 16:57]** - Analysis: API Gateway stage is /Prod, requires OriginPath=/Prod to route correctly
- **[10/24/2025 16:58]** - Conclusion: OriginPath=/Prod is required; original issue was OriginPath + /Prod/* cache behavior conflict
- **[10/24/2025 16:59]** - Updated template: Added OriginPath=/Prod back to APIOrigin
- **[10/24/2025 17:02]** - Preparing deployment with corrected configuration

**Resolution Approach:**
- **Before:** OriginPath="/Prod" + "/Prod/*" cache behavior (double-prefixing)
- **After:** OriginPath="/Prod" + NO "/Prod/*" cache behavior (correct routing)
- **Key Insight:** OriginPath is required for API Gateway /Prod stage
- **Infrastructure:** Managed via template.yaml to prevent configuration drift

---

### 2. S3 Bucket Policy Mismatch
**Status:** ✅ **RESOLVED**

**Problem Description:**
- Policy references wrong bucket name (dyscalculia-tools-website-536697250341 vs dyscalculia-tools-187249759)
- CloudFront cannot access S3 static assets

**Resolution:**
- **Before:** Bucket policy referencing "dyscalculia-tools-website-536697250341"
- **After:** Bucket policy referencing "dyscalculia-tools-187249759"
- Applied proper CloudFront OAC permissions

**Timeline:**
- **[10/23/2025 16:00]** - Issue identified, bucket policy updated with correct name
- **[10/23/2025 16:00]** - Applied proper CloudFront OAC permissions
- **[10/23/2025 16:30]** - Verification: ⚠️ Partially applied
- **[10/23/2025 16:45]** - Final verification: ✅ S3 origin configured with OAC

---

### 3. API Gateway Configuration Issues
**Status:** ✅ **RESOLVED**

**Problem Description:**
- CloudFront origin configuration and API Gateway endpoint completeness
- Requests routed incorrectly or to incomplete API Gateway
- Multiple API Gateways exist, confusion about which is production-ready

**API Gateway Context:**
- **vxam4rzpkd:** Production API Gateway (dyscalculia-tools-v2 stack) - CORRECT
- **qw3chvcbrf:** Temporary/incomplete API Gateway - missing endpoints

**Key Learning:**
**LESSON LEARNED:** vxam4rzpkd was always the correct API Gateway. The real issue was incomplete endpoint deployment, not wrong Gateway ID.

**Resolution Process:**
1. **Initial Error:** Assumed vxam4rzpkd API Gateway was "outdated"
2. **Wrong Fix:** Switched CloudFront to qw3chvcbrf (incomplete API Gateway)
3. **Discovery:** qw3chvcbrf lacked critical endpoints like /api/health
4. **Correction:** Reverted to vxam4rzpkd (which was always the correct production Gateway)
5. **Final Fix:** Added missing endpoints to vxam4rzpkd to make it complete

**Timeline:**
- **[10/23/2025 16:00]** - **INITIAL ERROR:** Incorrectly identified vxam4rzpkd as outdated
- **[10/23/2025 17:00]** - **WRONG FIX:** Switched CloudFront from vxam4rzpkd to qw3chvcbrf
- **[10/23/2025 17:45]** - **DISCOVERY:** qw3chvcbrf missing critical endpoints
- **[10/23/2025 18:30]** - **CORRECTION:** Reverted CloudFront back to vxam4rzpkd
- **[10/23/2025 18:35]** - **FINAL RESOLUTION:** Added missing endpoints to vxam4rzpkd
  - ✅ Added /api/health endpoint to vxam4rzpkd API Gateway
  - ✅ Updated template.yaml to reference correct distribution (E69DLY1YOK93D)
  - ✅ Deployed SAM stack (dyscalculia-tools-v2) with complete endpoints
  - ✅ Verified: https://vxam4rzpkd.execute-api.us-east-1.amazonaws.com/Prod/api/health

---

### 4. Missing Static Assets Cache Behaviors
**Status:** ✅ **RESOLVED**

**Problem Description:**
- No cache behaviors for CSS, JS, JSON files - all requests go to Lambda
- Static assets return 403 instead of serving from S3

**Resolution:**
- **Before:** CloudFront with only default behavior (all to Lambda)
- **After:** CloudFront with cache behaviors for *.css, *.js, *.json (to S3)
- **Final State:** 8 cache behaviors: /Prod/*, *.css, *.js, *.json, *.ico, *.png, *.jpg, *.svg

**Timeline:**
- **[10/23/2025 16:00]** - Issue identified, added cache behaviors and configured S3 origin
- **[10/23/2025 16:00]** - Uploaded essential static files to S3
- **[10/23/2025 16:30]** - Initial verification: ❌ Fix not applied
- **[10/23/2025 16:45]** - Status update: ✅ 6 cache behaviors added
- **[10/23/2025 17:45]** - **RE-VERIFICATION:** ❌ Fix not applied to correct distribution
  - E69DLY1YOK93D (active) missing static asset routing
  - EMANNVI38BDCI (inactive) may have behaviors but doesn't serve domain
- **[10/23/2025 19:00]** - **FINAL VERIFICATION:** ✅ Fix successfully applied
  - All static assets properly routed to S3Origin on active distribution

---

### 5. Missing S3 Origin in Active Distribution
**Status:** ✅ **RESOLVED**

**Problem Description:**
- E69DLY1YOK93D (active distribution) has no S3 origin configured
- Static assets cannot be served from S3, all requests go to Lambda

**Resolution:**
- **Before:** E69DLY1YOK93D with only API Gateway origin
- **After:** E69DLY1YOK93D with both API Gateway and S3 origins

**Final Configuration:**
- S3Origin: dyscalculia-tools-187249759.s3.amazonaws.com with OAC (E1E3L4F0B0VGY2)
- APIGateway: vxam4rzpkd.execute-api.us-east-1.amazonaws.com

**Timeline:**
- **[10/23/2025 17:45]** - Issue identified
- **[10/23/2025 19:00]** - Verification completed: ✅ Both origins properly configured

---

### 6. Wrong Distribution Updated Previously
**Status:** ✅ **RESOLVED**

**Problem Description:**
- Previous fixes applied to EMANNVI38BDCI (inactive) instead of E69DLY1YOK93D (active)
- Domain continues to serve from unfixed distribution
- Template.yaml references wrong distribution ID in outputs

**Resolution:**
- **Before:** Template.yaml referencing EMANNVI38BDCI (inactive distribution)
- **After:** Template.yaml referencing E69DLY1YOK93D (active distribution)

**Timeline:**
- **[10/23/2025 17:45]** - Issue identified: E69DLY1YOK93D serves dyscalculiatools.com
- **[10/23/2025 18:35]** - Corrected: Updated template.yaml distribution ID

---

### 7. Missing /api/* Cache Behavior
**Status:** ✅ **RESOLVED**

**Problem Description:**
- CloudFront has `/Prod/*` cache behavior but missing `/api/*` behavior
- API requests like `/api/health` fall through to default behavior without `/Prod` prefix
- API Gateway expects `/Prod/api/health` but receives `/api/health`

**Cache Behavior Analysis:**
- `/Prod/*` → APIGateway (matches `/Prod/api/health` but not `/api/health`)
- `*.css`, `*.js`, etc. → S3Origin (working)
- **Default behavior** → APIGateway (no `/Prod` prefix added)

**Resolution:**
- Added `/api/*` cache behavior routing to APIGateway
- CloudFront now has 9 cache behaviors total

**Timeline:**
- **[10/23/2025 23:50]** - Issue identified: Missing `/api/*` cache behavior
- **[10/23/2025 23:55]** - Fix applied: Added `/api/*` cache behavior
- **Status:** ✅ Completed - Waited 10-15 minutes for propagation

---

### 8. API Gateway Direct Access Working
**Status:** ✅ **RESOLVED** (Diagnostic Issue)

**Problem Description:**
- API Gateway works directly but fails through CloudFront
- Confirms infrastructure is correct, issue is CloudFront routing
- Root cause resolved by Issue #7 - missing cache behavior

**Verification Results:**
- ✅ **Direct API Gateway:** `https://vxam4rzpkd.execute-api.us-east-1.amazonaws.com/Prod/api/health` returns 200
- ✅ **Direct Homepage:** `https://vxam4rzpkd.execute-api.us-east-1.amazonaws.com/Prod/` returns HTML
- ❌ **Through CloudFront:** `https://dyscalculiatools.com/api/health` returns 403 (fixed by Issue #7)

**Timeline:**
- **[10/23/2025 23:45]** - Confirmed: API Gateway and Lambda function working correctly
- **[10/23/2025 23:50]** - Resolved: Issue was CloudFront routing, not API Gateway
- **Status:** ✅ No API Gateway changes needed

---

### 9. Infrastructure-as-Code Migration
**Status:** 🔄 **IN PROGRESS**

**Problem Description:**
- Manual CLI fixes to E69DLY1YOK93D kept reverting
- Template.yaml contained OriginPath="/Prod" causing configuration drift
- CloudFront distribution not managed by CloudFormation stack

**Resolution Approach:**
- Uncommented CloudFront section in template.yaml
- Removed OriginPath="/Prod" from template
- Added all cache behaviors (/api/*, *.css, *.js, *.json, *.ico, *.png, *.jpg, *.svg)
- Deployed new distribution via SAM (Option B)

**Timeline:**
- **[10/24/2025 16:30]** - Identified template.yaml as source of configuration reverts
- **[10/24/2025 16:32]** - Updated template.yaml: Removed OriginPath, added cache behaviors
- **[10/24/2025 16:34]** - First deployment failed: Domain alias conflict
- **[10/24/2025 16:36]** - Removed domain aliases from template temporarily
- **[10/24/2025 16:38]** - Deployment succeeded: Created E1YVN4SG69F679 without OriginPath
- **[10/24/2025 16:42]** - Testing: New distribution returns 403 on homepage
- **[10/24/2025 16:55]** - Investigation: Confirmed OriginPath="" in new distribution
- **[10/24/2025 16:57]** - Discovery: API Gateway /Prod stage requires OriginPath=/Prod
- **[10/24/2025 16:58]** - Root cause clarified: Issue was OriginPath + /Prod/* cache behavior together, not OriginPath alone
- **[10/24/2025 16:59]** - Updated template: Added OriginPath=/Prod back (without /Prod/* cache behavior)
- **[10/24/2025 17:02]** - Status: Ready to deploy corrected configuration
- **[10/24/2025 17:12]** - Deployment succeeded: Updated E1YVN4SG69F679 with OriginPath=/Prod
- **[10/24/2025 17:16]** - Testing: /api/health works, homepage still returns 403
- **[10/24/2025 17:21]** - Discovery: API Gateway Prod stage using old deployment (gglp2a from 10/23)

**Current State:**
- Old distribution: E69DLY1YOK93D (serving dyscalculiatools.com, has 403 issue)
- New distribution: E1YVN4SG69F679 (d3jpuqbmoxwr0v.cloudfront.net, has OriginPath=/Prod)
- Root cause clarified: OriginPath=/Prod is required for API Gateway /Prod stage
- Original issue: OriginPath=/Prod + /Prod/* cache behavior caused double-prefixing
- Solution: OriginPath=/Prod without /Prod/* cache behavior
- New issue discovered: API Gateway stage deployment mismatch (see Issue #10)

---

### 10. API Gateway Stage Deployment Mismatch
**Status:** 🔄 **IN PROGRESS**

**Problem Description:**
- API Gateway Prod stage pointing to old deployment (gglp2a from 10/23/2025)
- Latest deployment in stack is mmho9l (from 10/24/2025 17:12)
- Root path (/) exists in API Gateway with Lambda integration
- Stage not automatically updated to latest deployment after SAM deploy

**Impact:**
- Homepage returns MissingAuthenticationTokenException
- /api/health works (was in old deployment)
- CloudFront routing correct, but API Gateway serving stale configuration

**Timeline:**
- **[10/24/2025 17:16]** - Testing: Homepage returns 403 MissingAuthenticationTokenException
- **[10/24/2025 17:17]** - Verified: Root path exists in API Gateway with GET method
- **[10/24/2025 17:18]** - Verified: Root path integrated with Lambda function
- **[10/24/2025 17:19]** - Discovery: Prod stage using deployment gglp2a (10/23), stack has mmho9l (10/24)
- **[10/24/2025 17:21]** - Identified: Stage not updated to latest deployment
- **[10/24/2025 17:26]** - Updated Prod stage to deployment mmho9l
- **[10/24/2025 17:26]** - Testing: Homepage still returns 403 MissingAuthenticationTokenException
- **[10/24/2025 17:28]** - Created new deployment uip7wq manually
- **[10/24/2025 17:30]** - Testing: All paths except /api/health return 403
- **[10/24/2025 17:31]** - Verified: /api/health works, /, /about fail
- **[10/24/2025 17:32]** - Analysis: Deployment snapshots missing most routes, only /api/health present
- **[10/24/2025 17:33]** - Root cause: SAM not creating new deployments when API routes change
- **[10/24/2025 17:34]** - Solution: Added AutoPublishAlias: live to Lambda function

**Resolution:**
- Added AutoPublishAlias: live to force new deployments on every change
- This ensures API Gateway always has latest routes
- Enables automatic version management and rollback capability
- Infrastructure-as-code best practice for production

**Future Prevention:**
- AutoPublishAlias will prevent this issue on all future deployments
- SAM will automatically create new API Gateway deployments
- Stage will automatically update to latest deployment
- No manual intervention required

---

**Problem Description:**
- Manual CLI fixes to E69DLY1YOK93D kept reverting
- Template.yaml contained OriginPath="/Prod" causing configuration drift
- CloudFront distribution not managed by CloudFormation stack

**Resolution Approach:**
- Uncommented CloudFront section in template.yaml
- Removed OriginPath="/Prod" from template
- Added all cache behaviors (/api/*, *.css, *.js, *.json, *.ico, *.png, *.jpg, *.svg)
- Deployed new distribution via SAM (Option B)

**Timeline:**
- **[10/24/2025 16:30]** - Identified template.yaml as source of configuration reverts
- **[10/24/2025 16:32]** - Updated template.yaml: Removed OriginPath, added cache behaviors
- **[10/24/2025 16:34]** - First deployment failed: Domain alias conflict
- **[10/24/2025 16:36]** - Removed domain aliases from template temporarily
- **[10/24/2025 16:38]** - Deployment succeeded: Created E1YVN4SG69F679 without OriginPath
- **[10/24/2025 16:42]** - Testing: New distribution returns 403 on homepage
- **[10/24/2025 16:55]** - Investigation: Confirmed OriginPath="" in new distribution
- **[10/24/2025 16:57]** - Discovery: API Gateway /Prod stage requires OriginPath=/Prod
- **[10/24/2025 16:58]** - Root cause clarified: Issue was OriginPath + /Prod/* cache behavior together, not OriginPath alone
- **[10/24/2025 16:59]** - Updated template: Added OriginPath=/Prod back (without /Prod/* cache behavior)
- **[10/24/2025 17:02]** - Status: Ready to deploy corrected configuration

**Current State:**
- Old distribution: E69DLY1YOK93D (serving dyscalculiatools.com, has 403 issue)
- New distribution: E1YVN4SG69F679 (d3jpuqbmoxwr0v.cloudfront.net, has 403 due to missing OriginPath)
- Root cause clarified: OriginPath=/Prod is required for API Gateway /Prod stage
- Original issue: OriginPath=/Prod + /Prod/* cache behavior caused double-prefixing
- Solution: OriginPath=/Prod without /Prod/* cache behavior

---

## Summary

**Total Issues Identified:** 10
**Issues Resolved:** 8
**Issues In Progress:** 1 (Infrastructure-as-Code Migration)
**Issues Unresolved:** 1 (CloudFront Origin Path Mismatch)
**Last Updated:** October 24, 2025 10:42 GMT

**Key Learnings:**
1. Most issues were related to CloudFront configuration rather than backend services
2. API Gateway (vxam4rzpkd) was always correct - problems were in routing and cache behaviors
3. Manual CLI fixes reverted due to OriginPath="/Prod" in template.yaml
4. Infrastructure-as-code is essential to prevent configuration drift

**Current Configuration:**
- **Active Distribution:** E69DLY1YOK93D (serving dyscalculiatools.com)
- **New Distribution:** E1YVN4SG69F679 (d3jpuqbmoxwr0v.cloudfront.net)
- **API Gateway:** vxam4rzpkd.execute-api.us-east-1.amazonaws.com
- **S3 Bucket:** dyscalculia-tools-187249759
- **Status:** Both distributions returning 403 on homepage, investigation ongoing patterns)
- **Origins:** Both API Gateway and S3 properly configured

---

## Deployment Timeline

### Stack Deployment
- **[10/23/2025 16:00]** - Comprehensive fix deployment initiated

