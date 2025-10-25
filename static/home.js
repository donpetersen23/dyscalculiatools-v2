
function showTools() {
    document.getElementById('tools-section').style.display = 'block';
    document.getElementById('research-section').style.display = 'none';
    document.querySelectorAll('.action-buttons .btn')[0].classList.add('active');
    document.querySelectorAll('.action-buttons .btn')[1].classList.remove('active');
}

function showResearch() {
    document.getElementById('tools-section').style.display = 'none';
    document.getElementById('research-section').style.display = 'block';
    document.querySelectorAll('.action-buttons .btn')[1].classList.add('active');
    document.querySelectorAll('.action-buttons .btn')[0].classList.remove('active');
}

let toolsData = [];
let researchData = [];

fetch('/tools_data.json')
    .then(response => response.json())
    .then(data => { toolsData = data; })
    .catch(error => console.error('Error loading tools data:', error));

fetch('/research_metadata.json')
    .then(response => response.json())
    .then(data => { researchData = data; })
    .catch(error => console.error('Error loading research data:', error));

function searchTools() {
    const query = document.getElementById('tools-search').value.toLowerCase();
    if (!query.trim()) {
        document.getElementById('tools-results').innerHTML = '';
        return;
    }
    
    const results = toolsData.filter(tool => 
        tool.title.toLowerCase().includes(query) ||
        tool.description.toLowerCase().includes(query) ||
        tool.tags.some(tag => tag.toLowerCase().includes(query)) ||
        tool.challenges.some(challenge => challenge.toLowerCase().includes(query))
    );
    
    displayToolsResults(results);
}

function quickSearchTools(query) {
    document.getElementById('tools-search').value = query;
    const results = toolsData.filter(tool => 
        tool.title.toLowerCase().includes(query.toLowerCase()) ||
        tool.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())) ||
        tool.challenges.some(challenge => challenge.toLowerCase().includes(query.toLowerCase()))
    );
    displayToolsResults(results);
}

function displayToolsResults(results) {
    const resultsDiv = document.getElementById('tools-results');
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = '<p>No tools found matching your search.</p>';
        return;
    }
    
    let html = '<div class="results-count">Found ' + results.length + ' tools and strategies</div>';
    results.forEach(tool => {
        html += `
            <div class="card card-success">
                <h3 class="item-title">${tool.title}</h3>
                <p class="item-description">${tool.description}</p>
                <div class="item-details">
                    <p><strong>Age Range:</strong> ${tool.age_range}</p>
                    <p><strong>Setting:</strong> ${tool.setting}</p>
                    <p><strong>Time Required:</strong> ${tool.time_required}</p>
                    <p><strong>Materials:</strong> ${tool.materials}</p>
                </div>
                <div class="item-steps">
                    <h4>How to Use:</h4>
                    <ol>
                        ${tool.steps.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                </div>
                <div>
                    ${tool.tags.map(tag => `<span class="tag tag-success">${tag}</span>`).join(' ')}
                </div>
            </div>
        `;
    });
    resultsDiv.innerHTML = html;
}

function searchResearch() {
    const query = document.getElementById('research-search').value.toLowerCase();
    if (!query.trim()) {
        document.getElementById('search-results').innerHTML = '';
        return;
    }
    
    const results = researchData.filter(item => 
        item.title.toLowerCase().includes(query) ||
        item.authors.toLowerCase().includes(query) ||
        item.summary.toLowerCase().includes(query) ||
        item.tags.some(tag => tag.toLowerCase().includes(query)) ||
        (item.keywords && item.keywords.some(keyword => keyword.toLowerCase().includes(query)))
    );
    
    displayResults(results);
}

function quickSearch(query) {
    document.getElementById('research-search').value = query;
    const results = researchData.filter(item => 
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())) ||
        (item.keywords && item.keywords.some(keyword => keyword.toLowerCase().includes(query.toLowerCase())))
    );
    displayResults(results);
}

function displayResults(data) {
    const resultsDiv = document.getElementById('search-results');
    if (!data || data.length === 0) {
        resultsDiv.innerHTML = '<p>No research found matching your search.</p>';
        return;
    }
    
    let html = '<div class="results-count">Found ' + data.length + ' research studies</div>';
    data.forEach(item => {
        html += `
            <div class="card">
                <h3>${item.title}</h3>
                <p style="color: #666; font-size: 0.95rem;">${item.authors}</p>
                <p>${item.summary}</p>
                <div>
                    ${item.tags.map(tag => `<span class="tag">${tag}</span>`).join(' ')}
                </div>
            </div>
        `;
    });
    resultsDiv.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', function() {
    showTools();
    
    document.getElementById('tools-search').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') searchTools();
    });
    
    document.getElementById('research-search').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') searchResearch();
    });
});
