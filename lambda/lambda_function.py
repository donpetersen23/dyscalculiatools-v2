import json
import os

CDN_URL = os.environ.get('CDN_URL', 'https://your-cloudfront-domain.cloudfront.net')

COMPONENTS = {
    'header': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="apple-touch-icon" sizes="180x180" href="{cdn}/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="{cdn}/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="{cdn}/favicon-16x16.png">
    <link rel="shortcut icon" href="{cdn}/favicon.ico">
    <link rel="stylesheet" href="{cdn}/styles.css">
</head>
<body>
    <header>
        <h1>Dyscalculia Tools</h1>
        <p>Evidence-Based Techniques for Dyscalculia</p>
        <div class="auth-buttons">
            <button class="btn btn-primary btn-auth" id="auth-btn" onclick="showSignup()">Sign In / Sign Up</button>
            <div id="user-menu" style="display: none;">
                <span id="username-display"></span>
                <button class="btn btn-primary btn-auth" onclick="logout()">Logout</button>
            </div>
        </div>
    </header>
    <main>''',
    
    'footer': '''    </main>
    <footer>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </nav>
    </footer>
    
    <div id="login-modal" class="modal" style="display: none;">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal('login-modal')">&times;</span>
            <h2>Login</h2>
            <form id="login-form">
                <input type="email" placeholder="Email" required>
                <input type="password" placeholder="Password" required>
                <button class="btn btn-primary" type="submit">Login</button>
            </form>
            <p>Don't have an account? <a href="#" onclick="closeModal('login-modal'); showSignup();">Sign up</a></p>
        </div>
    </div>
    
    <div id="signup-modal" class="modal" style="display: none;">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal('signup-modal')">&times;</span>
            <h2>Join the Community</h2>
            <form id="signup-form">
                <input type="text" placeholder="Name" required>
                <input type="email" placeholder="Email" required>
                <select required>
                    <option value="">I am a...</option>
                    <option value="parent">Parent</option>
                    <option value="teacher">Teacher</option>
                    <option value="tutor">Tutor</option>
                    <option value="researcher">Researcher</option>
                    <option value="individual">Individual with dyscalculia</option>
                    <option value="other">Other</option>
                </select>
                <input type="password" placeholder="Password" required>
                <button class="btn btn-primary" type="submit">Join Community</button>
            </form>
            <p>Already have an account? <a href="#" onclick="closeModal('signup-modal'); showLogin();">Login</a></p>
        </div>
    </div>
    
    <script src="{cdn}/common.js"></script>
    {page_script}
</body>
</html>'''
}

PAGES = {
    '/': {
        'title': 'Dyscalculia Tools',
        'body': '''<section class="action-buttons">
    <button class="btn btn-primary" onclick="showTools()">Tools & Strategies</button>
    <button class="btn btn-primary" onclick="showResearch()">Research & Evidence</button>
</section>

<div class="content-container">
    <div id="tools-section" class="content-section">
        <h2>Search Tools & Strategies</h2>
        <p style="text-align: center; margin-bottom: 2rem; color: #666;">Find evidence-based tools and strategies for specific dyscalculia challenges</p>
        
        <div class="search-container">
            <input type="text" id="tools-search" placeholder="Search for tools, strategies, or challenges..." />
            <button class="btn btn-primary" onclick="searchTools()">Search</button>
        </div>
        
        <div class="tag-container">
            <h3>Browse by Category:</h3>
            <div class="tag-list">
                <button class="tag tag-success" onclick="quickSearchTools('Multiplication Facts')">Multiplication Facts</button>
                <button class="tag tag-success" onclick="quickSearchTools('Number Sense')">Number Sense</button>
                <button class="tag tag-success" onclick="quickSearchTools('Math Anxiety')">Math Anxiety</button>
                <button class="tag tag-success" onclick="quickSearchTools('Word Problems')">Word Problems</button>
                <button class="tag tag-success" onclick="quickSearchTools('Fractions')">Fractions</button>
                <button class="tag tag-success" onclick="quickSearchTools('Self-Esteem')">Self-Esteem</button>
            </div>
        </div>
        
        <div id="tools-results" class="results-section"></div>
    </div>
    
    <div id="research-section" class="content-section" style="display: none;">
        <h2>Search Dyscalculia Research</h2>
        <p style="text-align: center; margin-bottom: 2rem; color: #666;">Explore our curated database of research studies specifically relevant to dyscalculia</p>
        
        <div class="search-container">
            <input type="text" id="research-search" placeholder="Search for interventions, strategies, or topics..." />
            <button class="btn btn-primary" onclick="searchResearch()">Search</button>
        </div>
        
        <div class="tag-container">
            <h3>Browse by Topic:</h3>
            <div class="tag-list">
                <button class="tag" onclick="quickSearch('multiplication facts')">Multiplication Facts</button>
                <button class="tag" onclick="quickSearch('number sense')">Number Sense</button>
                <button class="tag" onclick="quickSearch('math anxiety')">Math Anxiety</button>
                <button class="tag" onclick="quickSearch('visual strategies')">Visual Strategies</button>
                <button class="tag" onclick="quickSearch('working memory')">Working Memory</button>
                <button class="tag" onclick="quickSearch('interventions')">Interventions</button>
            </div>
        </div>
        
        <div id="search-results" class="results-section"></div>
    </div>
</div>''',
        'script': f'<script src="{CDN_URL}/home.js"></script>'
    },
    '/about': {
        'title': 'About - Dyscalculia Tools',
        'body': '<section class="content-container"><h2>About Dyscalculia Tools</h2><p>Your about content here...</p></section>',
        'script': ''
    },
    '/contact': {
        'title': 'Contact - Dyscalculia Tools',
        'body': '<section class="content-container"><h2>Contact Us</h2><p>Your contact content here...</p></section>',
        'script': ''
    }
}

def lambda_handler(event, context):
    path = event.get('rawPath', event.get('path', '/'))
    
    page = PAGES.get(path)
    if not page:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>404 - Page Not Found</h1>'
        }
    
    html = COMPONENTS['header'].format(title=page['title'], cdn=CDN_URL)
    html += page['body']
    html += COMPONENTS['footer'].format(cdn=CDN_URL, page_script=page['script'])
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8'},
        'body': html
    }
