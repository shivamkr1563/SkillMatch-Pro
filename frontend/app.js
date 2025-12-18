/**
 * SkillMatch Pro Frontend Application
 */

// API Configuration
// Update this URL after deploying to Render
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://skillmatch-pro-api.onrender.com';

// State
let currentQuery = '';
let currentResults = [];

// DOM Elements
const queryInput = document.getElementById('queryInput');
const searchBtn = document.getElementById('searchBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');
const resultsTable = document.getElementById('resultsTable');
const resultsCount = document.getElementById('resultsCount');
const exportBtn = document.getElementById('exportBtn');
const exampleChips = document.querySelectorAll('.chip');

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSearch();
    }
});

exampleChips.forEach(chip => {
    chip.addEventListener('click', (e) => {
        const query = e.target.getAttribute('data-query');
        queryInput.value = query;
        handleSearch();
    });
});

exportBtn.addEventListener('click', exportToCSV);

/**
 * Handle search request
 */
async function handleSearch() {
    const query = queryInput.value.trim();
    
    if (!query) {
        showError('Please enter a job description or requirements');
        return;
    }
    
    if (query.length < 10) {
        showError('Please provide more details in your query (at least 10 characters)');
        return;
    }
    
    currentQuery = query;
    
    // Update UI
    setLoading(true);
    hideError();
    hideResults();
    
    try {
        const recommendations = await fetchRecommendations(query);
        displayResults(recommendations);
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

/**
 * Fetch recommendations from API
 */
async function fetchRecommendations(query) {
    const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch recommendations');
    }
    
    const data = await response.json();
    return data;
}

/**
 * Display results in a table
 */
function displayResults(data) {
    currentResults = data.recommendations;
    
    if (!currentResults || currentResults.length === 0) {
        showError('No recommendations found. Try rephrasing your query.');
        return;
    }
    
    // Update count
    resultsCount.textContent = `Found ${data.count} assessment${data.count > 1 ? 's' : ''} matching your requirements`;
    
    // Build table
    let tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Assessment Name</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    currentResults.forEach((rec, index) => {
        tableHTML += `
            <tr>
                <td class="index-cell">${index + 1}</td>
                <td class="name-cell">
                    <div class="assessment-name">${escapeHtml(rec.assessment_name)}</div>
                </td>
                <td class="action-cell">
                    <a href="${escapeHtml(rec.assessment_url)}" 
                       target="_blank" 
                       rel="noopener noreferrer" 
                       class="btn-link">
                        View Details →
                    </a>
                </td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    resultsTable.innerHTML = tableHTML;
    resultsSection.style.display = 'block';
}

/**
 * Export results to CSV
 */
function exportToCSV() {
    if (!currentResults || currentResults.length === 0) {
        return;
    }
    
    let csvContent = 'Query,Assessment_url\n';
    
    currentResults.forEach(rec => {
        const query = `"${currentQuery.replace(/"/g, '""')}"`;
        const url = rec.assessment_url;
        csvContent += `${query},${url}\n`;
    });
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'shl_recommendations.csv');
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * UI Helper Functions
 */
function setLoading(isLoading) {
    if (isLoading) {
        searchBtn.disabled = true;
        document.querySelector('.btn-text').style.display = 'none';
        document.querySelector('.btn-loader').style.display = 'inline';
        loadingIndicator.style.display = 'block';
    } else {
        searchBtn.disabled = false;
        document.querySelector('.btn-text').style.display = 'inline';
        document.querySelector('.btn-loader').style.display = 'none';
        loadingIndicator.style.display = 'none';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Check API health on load
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✓ API is healthy');
        } else {
            console.warn('⚠ API health check failed');
        }
    } catch (error) {
        console.error('✗ Cannot connect to API:', error);
        showError('Cannot connect to API. Please ensure the backend server is running.');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAPIHealth();
});
