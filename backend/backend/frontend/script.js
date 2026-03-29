// Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Get API key from input or localStorage
function getApiKey() {
    return document.getElementById('apiKey').value || localStorage.getItem('hubspot_api_key');
}

// Save API key to localStorage
function saveApiKey() {
    const apiKey = document.getElementById('apiKey').value;
    if (apiKey) {
        localStorage.setItem('hubspot_api_key', apiKey);
    }
}

// Test connection
async function testConnection() {
    const apiKey = getApiKey();
    if (!apiKey) {
        showStatus('connectionStatus', 'error', 'Please enter your API key');
        return;
    }

    showStatus('connectionStatus', 'info', 'Testing connection...');

    try {
        const response = await fetch(`${API_BASE_URL}/test-connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_key: apiKey })
        });

        const data = await response.json();

        if (response.ok) {
            showStatus('connectionStatus', 'success', '✓ Connection successful!');
            saveApiKey();
        } else {
            showStatus('connectionStatus', 'error', `✗ Connection failed: ${data.message}`);
        }
    } catch (error) {
        showStatus('connectionStatus', 'error', `✗ Error: ${error.message}`);
    }
}

// Execute natural language command
async function executeCommand() {
    const command = document.getElementById('commandInput').value.trim();
    const apiKey = getApiKey();

    if (!command) {
        showStatus('commandStatus', 'error', 'Please enter a command');
        return;
    }

    if (!apiKey) {
        showStatus('commandStatus', 'error', 'Please set your HubSpot API key first');
        return;
    }

    showStatus('commandStatus', 'info', 'Executing command...');
    updateResults('Processing command...');

    try {
        const response = await fetch(`${API_BASE_URL}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: command,
                api_key: apiKey
            })
        });

        const data = await response.json();

        if (response.ok) {
            showStatus('commandStatus', 'success', '✓ Command executed successfully');
            updateResults(JSON.stringify(data, null, 2));
        } else {
            showStatus('commandStatus', 'error', `✗ Error: ${data.message}`);
            updateResults(JSON.stringify(data, null, 2));
        }
    } catch (error) {
        showStatus('commandStatus', 'error', `✗ Error: ${error.message}`);
        updateResults(`Error: ${error.message}`);
    }
}

// Execute quick action
async function executeQuickAction(action) {
    const apiKey = getApiKey();

    if (!apiKey) {
        showStatus('commandStatus', 'error', 'Please set your HubSpot API key first');
        return;
    }

    let endpoint = '';
    let method = 'GET';

    switch (action) {
        case 'list_workflows':
            endpoint = '/workflows';
            break;
        case 'list_contacts':
            endpoint = '/contacts';
            break;
        case 'create_workflow':
            endpoint = '/workflows';
            method = 'POST';
            break;
        default:
            return;
    }

    showStatus('commandStatus', 'info', 'Executing action...');
    updateResults('Processing...');

    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (method === 'POST') {
            options.body = JSON.stringify({
                name: 'Quick Workflow',
                description: 'Created via JustQuick',
                api_key: apiKey
            });
        } else {
            endpoint += `?api_key=${encodeURIComponent(apiKey)}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const data = await response.json();

        if (response.ok) {
            showStatus('commandStatus', 'success', '✓ Action completed successfully');
            updateResults(JSON.stringify(data, null, 2));
        } else {
            showStatus('commandStatus', 'error', `✗ Error: ${data.message}`);
            updateResults(JSON.stringify(data, null, 2));
        }
    } catch (error) {
        showStatus('commandStatus', 'error', `✗ Error: ${error.message}`);
        updateResults(`Error: ${error.message}`);
    }
}

// Show status message
function showStatus(elementId, type, message) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `status-message ${type}`;
}

// Update results panel
function updateResults(content) {
    document.getElementById('resultsPanel').textContent = content;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Load saved API key if available
    const savedApiKey = localStorage.getItem('hubspot_api_key');
    if (savedApiKey) {
        document.getElementById('apiKey').value = savedApiKey;
    }

    // Allow Enter key to execute command
    document.getElementById('commandInput').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            executeCommand();
        }
    });
});
