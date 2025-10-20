#!/usr/bin/env python3
"""Build static HTML files from components"""
import os

def build_page(title, content_file, scripts_file, output_file):
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        html = f.read()
    with open(f'templates/{content_file}', 'r', encoding='utf-8') as f:
        content = f.read()
    with open(f'templates/{scripts_file}', 'r', encoding='utf-8') as f:
        scripts = f.read()
    
    html = html.replace('{{title}}', title)
    html = html.replace('{{content}}', content)
    html = html.replace('{{scripts}}', scripts)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Built {output_file}')

if __name__ == '__main__':
    build_page('Home', 'home-content.html', 'home-scripts.html', 'index.html')
    build_page('About', 'about-content.html', 'about-scripts.html', 'about.html')
    print('\nBuild complete!')
