# Component-Based Architecture

## Overview
Lambda dynamically assembles HTML pages from reusable components based on the URL requested.

## Structure

### Shared Components (Used on Every Page)
- **templates/base.html** - Contains `<head>`, `<header>`, `<footer>`, and placeholders:
  - `{{title}}` - Page title
  - `{{content}}` - Main page content
  - `{{scripts}}` - Page-specific JavaScript

### Page-Specific Components

#### Homepage (/)
- **templates/home-content.html** - Main content with tools/research sections
- **templates/home-scripts.html** - JavaScript for search functionality

#### About Page (/about)
- **templates/about-content.html** - About page content
- **templates/about-scripts.html** - Minimal JavaScript for modals

#### Tool Detail Pages (/tool/{id})
- **templates/tool_detail.html** - Tool detail component (already exists)

## How It Works

1. User requests a URL (e.g., `/` or `/about`)
2. Lambda receives the request
3. Lambda loads:
   - `base.html` (shared header/footer)
   - Page-specific content file
   - Page-specific scripts file
4. Lambda replaces placeholders in base.html
5. Lambda returns complete HTML page

## Benefits

✅ Single source of truth for header/footer
✅ Easy to update navigation across all pages
✅ Reduced code duplication
✅ Dynamic page generation
✅ Consistent look and feel

## Next Steps

1. Test locally with `app.py`
2. Deploy Lambda function with templates folder
3. Ensure templates are packaged with Lambda deployment
4. Test on AWS
