"""
HubSpot API Client for JustQuick Workflow Agent
Handles all API communications with HubSpot
"""

import requests
from typing import Dict, Any, List, Optional
from config import Config

class HubSpotClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.HUBSPOT_API_KEY
        self.base_url = Config.HUBSPOT_BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        if not self.api_key:
            raise ValueError("HubSpot API key not provided. Set HUBSPOT_API_KEY env variable.")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Generic method to make API requests"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.text else {'status': 'success'}
        
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'details': getattr(e.response, 'text', 'No details available')
            }
    
    # ========================
    # WORKFLOWS ENDPOINTS (v3)
    # ========================
    
    def list_workflows(self) -> Dict[str, Any]:
        """List all workflows"""
        return self._make_request('GET', f"{Config.AUTOMATION_API_V3}/workflows")
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get a specific workflow by ID"""
        return self._make_request('GET', f"{Config.AUTOMATION_API_V3}/workflows/{workflow_id}")
    
    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new workflow
        
        Args:
            workflow_data: Dictionary containing workflow configuration
                - name (str): Workflow name
                - enabled (bool): Is workflow enabled
                - enrollmentCriteria (dict): Trigger conditions
                - actions (list): Workflow actions
                - objectType (str): 'CONTACT', 'DEAL', etc.
        """
        return self._make_request('POST', f"{Config.AUTOMATION_API_V3}/workflows", data=workflow_data)
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow"""
        return self._make_request('PATCH', f"{Config.AUTOMATION_API_V3}/workflows/{workflow_id}", data=workflow_data)
    
    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete a workflow"""
        return self._make_request('DELETE', f"{Config.AUTOMATION_API_V3}/workflows/{workflow_id}")
    
    def enroll_contact_in_workflow(self, workflow_id: str, contact_id: str) -> Dict[str, Any]:
        """Enroll a contact in a workflow"""
        endpoint = f"{Config.AUTOMATION_API_V3}/workflows/{workflow_id}/enrollments"
        data = {'contactId': contact_id}
        return self._make_request('POST', endpoint, data=data)
    
    # ========================
    # CONTACTS ENDPOINTS
    # ========================
    
    def list_contacts(self, limit: int = 10) -> Dict[str, Any]:
        """List contacts"""
        params = {'limit': limit}
        return self._make_request('GET', f"{Config.CRM_API_V3}/objects/contacts", params=params)
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get a specific contact"""
        return self._make_request('GET', f"{Config.CRM_API_V3}/objects/contacts/{contact_id}")
    
    def search_contacts(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Search for contacts based on criteria"""
        endpoint = f"{Config.CRM_API_V3}/objects/contacts/search"
        return self._make_request('POST', endpoint, data=criteria)
    
    # ========================
    # DEALS ENDPOINTS
    # ========================
    
    def list_deals(self, limit: int = 10) -> Dict[str, Any]:
        """List deals"""
        params = {'limit': limit}
        return self._make_request('GET', f"{Config.CRM_API_V3}/objects/deals", params=params)
    
    def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """Get a specific deal"""
        return self._make_request('GET', f"{Config.CRM_API_V3}/objects/deals/{deal_id}")
    
    def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal"""
        endpoint = f"{Config.CRM_API_V3}/objects/deals"
        return self._make_request('POST', endpoint, data=deal_data)
    
    # ========================
    # COMPANIES ENDPOINTS
    # ========================
    
    def list_companies(self, limit: int = 10) -> Dict[str, Any]:
        """List companies"""
        params = {'limit': limit}
        return self._make_request('GET', f"{Config.CRM_API_V3}/objects/companies", params=params)
    
    def get_company(self, company_id: str) -> Dict[str, Any]:
        """Get a specific company"""
        return self._make_request('GET', f"{Config.CRM_API_V3}/objects/companies/{company_id}")
    
    # ========================
    # TEST CONNECTION
    # ========================
    
    def test_connection(self) -> Dict[str, Any]:
        """Test if API key is valid"""
        return self._make_request('GET', "/crm/v3/objects/contacts?limit=1")
