"""
JustQuick - HubSpot Workflow Agent
Main Flask application
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import config, Config
from hubspot_client import HubSpotClient
from command_parser import CommandParser
from workflow_engine import WorkflowEngine
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config.from_object(config['development'])

# Initialize HubSpot client
try:
    hubspot_client = HubSpotClient()
except ValueError as e:
    logger.warning(f"HubSpot client initialization warning: {e}")
    hubspot_client = None

# ========================
# API ENDPOINTS
# ========================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'JustQuick Workflow Agent',
        'version': '1.0.0'
    }), 200

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test HubSpot API connection"""
    data = request.json
    api_key = data.get('api_key') or Config.HUBSPOT_API_KEY
    
    try:
        client = HubSpotClient(api_key)
        result = client.test_connection()
        
        if 'error' in result:
            return jsonify({'status': 'error', 'message': result['error']}), 400
        
        return jsonify({'status': 'success', 'message': 'Connection successful'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/command', methods=['POST'])
def execute_command():
    """
    Execute a natural language command
    
    POST /api/command
    {
        "command": "create workflow to email new contacts",
        "api_key": "optional_api_key"
    }
    """
    try:
        data = request.json
        command = data.get('command', '').strip()
        api_key = data.get('api_key') or Config.HUBSPOT_API_KEY
        
        if not command:
            return jsonify({'status': 'error', 'message': 'Command is required'}), 400
        
        # Parse command
        parsed = CommandParser.parse(command)
        
        if parsed['status'] != 'success':
            return jsonify(parsed), 400
        
        # Initialize client with provided/default API key
        client = HubSpotClient(api_key)
        
        # Execute action
        action = parsed['action']
        params = parsed['params']
        
        result = _execute_action(client, action, params)
        
        return jsonify(result), 200 if result.get('status') == 'success' else 400
    
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """List all workflows"""
    try:
        api_key = request.args.get('api_key') or Config.HUBSPOT_API_KEY
        client = HubSpotClient(api_key)
        result = client.list_workflows()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """Create a new workflow"""
    try:
        data = request.json
        api_key = data.get('api_key') or Config.HUBSPOT_API_KEY
        
        client = HubSpotClient(api_key)
        
        # Build workflow
        workflow = WorkflowEngine.build_simple_workflow(
            name=data.get('name', 'New Workflow'),
            description=data.get('description', '')
        )
        
        result = client.create_workflow(workflow)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Workflow created successfully',
            'workflow': result
        }), 201
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """Get a specific workflow"""
    try:
        api_key = request.args.get('api_key') or Config.HUBSPOT_API_KEY
        client = HubSpotClient(api_key)
        result = client.get_workflow(workflow_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workflows/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    """Delete a workflow"""
    try:
        api_key = request.args.get('api_key') or Config.HUBSPOT_API_KEY
        client = HubSpotClient(api_key)
        result = client.delete_workflow(workflow_id)
        return jsonify({'status': 'success', 'message': 'Workflow deleted'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """List contacts"""
    try:
        api_key = request.args.get('api_key') or Config.HUBSPOT_API_KEY
        limit = request.args.get('limit', 10, type=int)
        client = HubSpotClient(api_key)
        result = client.list_contacts(limit)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/contacts/search', methods=['POST'])
def search_contacts():
    """Search contacts"""
    try:
        data = request.json
        api_key = data.get('api_key') or Config.HUBSPOT_API_KEY
        client = HubSpotClient(api_key)
        result = client.search_contacts(data.get('criteria', {}))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========================
# HELPER FUNCTION
# ========================

def _execute_action(client: HubSpotClient, action: str, params: Dict) -> Dict:
    """Execute the parsed action"""
    
    if action == 'list_workflows':
        result = client.list_workflows()
        if 'error' not in result:
            return {'status': 'success', 'message': 'Workflows retrieved', 'data': result}
        return result
    
    elif action == 'create_workflow':
        workflow = WorkflowEngine.build_workflow(
            name=params.get('name'),
            trigger_type=params.get('trigger_type', 'manual'),
            action_type=params.get('action_type', 'send_email')
        )
        result = client.create_workflow(workflow)
        if 'error' not in result:
            return {'status': 'success', 'message': 'Workflow created successfully', 'data': result}
        return result
    
    elif action == 'delete_workflow':
        return {'status': 'error', 'message': 'Workflow ID needed for deletion. Use GET /api/workflows to find it.'}
    
    elif action == 'list_contacts':
        result = client.list_contacts()
        if 'error' not in result:
            return {'status': 'success', 'message': 'Contacts retrieved', 'data': result}
        return result
    
    elif action == 'search_contacts':
        criteria = {
            'filterGroups': [{
                'filters': [{
                    'propertyName': 'firstname',
                    'operator': 'CONTAINS',
                    'value': params.get('criteria', '')
                }]
            }]
        }
        result = client.search_contacts(criteria)
        if 'error' not in result:
            return {'status': 'success', 'message': 'Search completed', 'data': result}
        return result
    
    else:
        return {'status': 'error', 'message': f'Action {action} not implemented'}

# ========================
# ERROR HANDLERS
# ========================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
