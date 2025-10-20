# Static Site Architecture - Complete Guide

## How It Works

```
User Request
    ↓
Route 53 (dyscalculiatools.com)
    ↓
CloudFront
    ├─→ S3 (HTML/CSS/JS/images)     [/ , /about, /styles.css, etc.]
    └─→ Lambda (API only)            [/api/search, /api/generate-brief]
```

## File Structure

```
templates/              # Components (source)
├── base.html          # Header/footer
├── home-content.html  # Homepage content
├── home-scripts.html  # Homepage JS
├── about-content.html # About content
└── about-scripts.html # About JS

Root/                  # Built files (deployed to S3)
├── index.html         # Built from components
├── about.html         # Built from components
├── styles.css         # Static
└── *.json            # Static
```

## Workflow

### 1. Local Development
```bash
python app.py
```
Visit http://localhost:5000

### 2. Build Static Files
```bash
python build.py
```
Generates index.html and about.html from components

### 3. Deploy Everything
```bash
deploy.bat
```
- Builds HTML files
- Deploys Lambda (API only)
- Uploads to S3
- Invalidates CloudFront cache

## Making Changes

### Update Header/Footer
1. Edit `templates/base.html`
2. Run `python build.py`
3. Run `deploy.bat`

### Update Homepage
1. Edit `templates/home-content.html` or `templates/home-scripts.html`
2. Run `python build.py`
3. Run `deploy.bat`

### Add New Page
1. Create `templates/newpage-content.html`
2. Create `templates/newpage-scripts.html`
3. Add to `build.py`:
   ```python
   build_page('New Page', 'newpage-content.html', 'newpage-scripts.html', 'newpage.html')
   ```
4. Run `python build.py`
5. Run `deploy.bat`

## CloudFront Behavior

CloudFront automatically routes:
- `/` → S3: index.html
- `/about` → S3: about.html
- `/styles.css` → S3: styles.css
- `/api/*` → Lambda function

## Benefits

✅ Fast - Static files served from S3/CloudFront edge
✅ Cheap - No Lambda costs for page views
✅ Scalable - CloudFront handles any traffic
✅ Simple - Components make updates easy
✅ Best practice - Industry standard approach
