"""
Workflow Engine for JustQuick
Constructs and manages HubSpot workflow templates
"""

from typing import Dict, Any, List
from datetime import datetime

class WorkflowEngine:
    
    # Workflow templates for common use cases
    TEMPLATES = {
        'send_email': {
            'name': 'Send Email Workflow',
            'objectType': 'CONTACT',
            'enabled': True,
            'actions': [
                {
                    'type': 'SEND_EMAIL',
                    'actions': [{
                        'actionType': 'SEND_EMAIL',
                        'stepId': '0',
                        'portalId': 0,
                        'delayMillis': 0,
                        'emailTemplate': {
                            'id': 'default'
                        }
                    }]
                }
            ]
        },
        'create_deal': {
            'name': 'Create Deal Workflow',
            'objectType': 'CONTACT',
            'enabled': True,
            'actions': [
                {
                    'type': 'DEAL_CREATE',
                    'actions': [{
                        'actionType': 'CREATE_ASSOCIATED_RECORD',
                        'stepId': '0',
                        'recordObjectType': 'deal'
                    }]
                }
            ]
        },
        'assign_task': {
            'name': 'Assign Task Workflow',
            'objectType': 'CONTACT',
            'enabled': True,
            'actions': [
                {
                    'type': 'ASSIGN_TASK',
                    'actions': [{
                        'actionType': 'ENGAGMENT_CREATE',
                        'stepId': '0',
                        'engagementType': 'TASK'
                    }]
                }
            ]
        }
    }
    
    @staticmethod
    def build_workflow(name: str, trigger_type: str, action_type: str, 
                       additional_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build a workflow configuration based on templates
        
        Args:
            name: Workflow name
            trigger_type: Type of trigger ('new_contact', 'new_deal', 'manual')
            action_type: Type of action ('send_email', 'create_deal', 'assign_task')
            additional_params: Additional parameters for customization
        
        Returns:
            Workflow configuration dict
        """
        
        workflow = {
            'name': name,
            'enabled': True,
            'objectType': 'CONTACT',
            'trigger': WorkflowEngine._build_trigger(trigger_type, additional_params or {}),
            'actions': WorkflowEngine._build_actions(action_type, additional_params or {})
        }
        
        return workflow
    
    @staticmethod
    def _build_trigger(trigger_type: str, params: Dict) -> Dict[str, Any]:
        """Build trigger configuration"""
        
        triggers = {
            'new_contact': {
                'type': 'ENROLLMENT_TRIGGER',
                'triggerType': 'ENROLLMENT',
                'enrollmentCriteria': {
                    'requiresEnrollmentCriteria': False
                }
            },
            'new_deal': {
                'type': 'WORKFLOW_TRIGGER',
                'triggerType': 'OBJECT_PROPERTY_CHANGE',
                'objectProperty': 'hs_createdate'
            },
            'email_received': {
                'type': 'WORKFLOW_TRIGGER',
                'triggerType': 'ENGAGEMENT_EVENT',
                'engagementType': 'EMAIL'
            },
            'manual': {
                'type': 'MANUAL_TRIGGER',
                'enrollmentCriteria': {
                    'requiresEnrollmentCriteria': False
                }
            }
        }
        
        return triggers.get(trigger_type, triggers['manual'])
    
    @staticmethod
    def _build_actions(action_type: str, params: Dict) -> List[Dict[str, Any]]:
        """Build action configuration"""
        
        actions = {
            'send_email': [
                {
                    'type': 'SEND_EMAIL',
                    'actionType': 'SEND_EMAIL',
                    'delayMillis': 0,
                    'template_id': params.get('template_id', 'default')
                }
            ],
            'create_deal': [
                {
                    'type': 'CREATE_ASSOCIATED_RECORD',
                    'recordObjectType': 'deal',
                    'properties': {
                        'dealname': params.get('deal_name', 'New Deal'),
                        'dealstage': params.get('deal_stage', 'qualifiedtobuy')
                    }
                }
            ],
            'assign_task': [
                {
                    'type': 'ENGAGMENT_CREATE',
                    'engagementType': 'TASK',
                    'taskProperties': {
                        'hs_task_subject': params.get('task_subject', 'Follow-up Task'),
                        'hs_task_status': 'NOT_STARTED'
                    }
                }
            ]
        }
        
        return actions.get(action_type, [])
    
    @staticmethod
    def build_simple_workflow(name: str, description: str) -> Dict[str, Any]:
        """
        Build a simple, basic workflow for quick creation
        
        Args:
            name: Workflow name
            description: Workflow description
        
        Returns:
            Basic workflow configuration
        """
        return {
            'name': name,
            'description': description,
            'enabled': True,
            'objectType': 'CONTACT',
            'trigger': {
                'type': 'MANUAL_TRIGGER',
                'enrollmentCriteria': {
                    'requiresEnrollmentCriteria': False
                }
            },
            'actions': []
        }
