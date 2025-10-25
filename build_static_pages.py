#!/usr/bin/env python3
"""
Build static HTML pages from templates.
Run this during deployment to generate static site files.
"""
import json
import os
from pathlib import Path

# Configuration
TEMPLATES_DIR = Path('templates')
STATIC_DIR = Path('static')
OUTPUT_DIR = STATIC_DIR  # Output HTML files to static folder
CDN_URL = 'https://dyscalculiatools.com'

def load_json_data(filename):
    """Load JSON data file."""
    filepath = STATIC_DIR / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def read_template(filename):
    """Read template file."""
    filepath = TEMPLATES_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def build_homepage():
    """Generate homepage HTML."""
    print("Building homepage...")
    template = read_template('homepage.html')
    
    # Replace CDN URLs
    html = template.replace('/styles.css', f'{CDN_URL}/styles.css')
    html = html.replace('/apple-touch-icon.png', f'{CDN_URL}/apple-touch-icon.png')
    html = html.replace('/favicon-32x32.png', f'{CDN_URL}/favicon-32x32.png')
    html = html.replace('/favicon-16x16.png', f'{CDN_URL}/favicon-16x16.png')
    html = html.replace('/favicon.ico', f'{CDN_URL}/favicon.ico')
    html = html.replace('/tools_data.json', f'{CDN_URL}/tools_data.json')
    html = html.replace('/research_metadata.json', f'{CDN_URL}/research_metadata.json')
    
    output_file = OUTPUT_DIR / 'index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] Created {output_file}")

def build_about_page():
    """Generate about page HTML."""
    print("Building about page...")
    template = read_template('about.html')
    
    # Replace CDN URLs
    html = template.replace('/styles.css', f'{CDN_URL}/styles.css')
    html = html.replace('/apple-touch-icon.png', f'{CDN_URL}/apple-touch-icon.png')
    html = html.replace('/favicon-32x32.png', f'{CDN_URL}/favicon-32x32.png')
    html = html.replace('/favicon-16x16.png', f'{CDN_URL}/favicon-16x16.png')
    html = html.replace('/favicon.ico', f'{CDN_URL}/favicon.ico')
    
    output_file = OUTPUT_DIR / 'about.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] Created {output_file}")

def build_contact_page():
    """Generate contact page HTML."""
    print("Building contact page...")
    
    # Use about.html as template and modify
    template = read_template('about.html')
    html = template.replace('<title>About - Dyscalculia Tools</title>', 
                           '<title>Contact - Dyscalculia Tools</title>')
    html = html.replace('<h2>Building Solutions for Dyscalculia</h2>', 
                       '<h2>Contact Us</h2>')
    
    # Replace content section
    old_content = template[template.find('<section class="welcome">'):template.find('</section>') + 10]
    new_content = '''<section class="welcome">
            <h2>Contact Us</h2>
            <p>We'd love to hear from you! Whether you have questions, suggestions, or want to share your experience with dyscalculia.</p>
            <p><strong>Email:</strong> contact@dyscalculiatools.com</p>
            <p><strong>Community:</strong> Join our growing community of parents, teachers, tutors, and researchers working together to support individuals with dyscalculia.</p>
        </section>'''
    
    html = html.replace(old_content, new_content)
    
    # Replace CDN URLs
    html = html.replace('/styles.css', f'{CDN_URL}/styles.css')
    html = html.replace('/apple-touch-icon.png', f'{CDN_URL}/apple-touch-icon.png')
    html = html.replace('/favicon-32x32.png', f'{CDN_URL}/favicon-32x32.png')
    html = html.replace('/favicon-16x16.png', f'{CDN_URL}/favicon-16x16.png')
    html = html.replace('/favicon.ico', f'{CDN_URL}/favicon.ico')
    
    output_file = OUTPUT_DIR / 'contact.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] Created {output_file}")

def main():
    """Build all static pages."""
    print("=" * 50)
    print("Building Static Pages")
    print("=" * 50)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Build pages
    build_homepage()
    build_about_page()
    build_contact_page()
    
    print("=" * 50)
    print("[OK] Build complete!")
    print(f"[OK] Generated {len(list(OUTPUT_DIR.glob('*.html')))} HTML files")
    print("=" * 50)

if __name__ == '__main__':
    main()
