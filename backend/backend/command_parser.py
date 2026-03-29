"""
Command Parser for JustQuick
Converts natural language commands into structured workflow operations
"""

import re
from typing import Dict, Any, Tuple

class CommandParser:
    
    # Command patterns
    PATTERNS = {
        'create_workflow': r'create\s+workflow\s+(?:to\s+)?(.+?)(?:\s+for\s+|$)',
        'list_workflows': r'list\s+workflows',
        'delete_workflow': r'delete\s+workflow\s+(.+)',
        'update_workflow': r'update\s+workflow\s+(.+?)\s+(?:to|with)\s+(.+)',
        'trigger_workflow': r'(?:trigger|run)\s+workflow\s+(.+?)\s+for\s+(.+)',
        'search_contacts': r'search\s+contacts\s+(?:where|for)\s+(.+)',
        'list_contacts': r'list\s+contacts',
        'get_contact': r'get\s+contact\s+(.+)',
    }
    
    @staticmethod
    def parse(command: str) -> Dict[str, Any]:
        """
        Parse a natural language command into structured action
        
        Args:
            command (str): User's natural language command
            
        Returns:
            Dict with 'action', 'params', and 'status'
        """
        command = command.strip().lower()
        
        # Try to match patterns
        for action, pattern in CommandParser.PATTERNS.items():
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                params = CommandParser._extract_params(action, match, command)
                return {
                    'status': 'success',
                    'action': action,
                    'params': params,
                    'original_command': command
                }
        
        return {
            'status': 'error',
            'error': 'Command not recognized',
            'original_command': command,
            'hint': 'Try: "list workflows", "create workflow", "delete workflow", "search contacts"'
        }
    
    @staticmethod
    def _extract_params(action: str, match, command: str) -> Dict[str, Any]:
        """Extract parameters from matched groups"""
        params = {}
        
        if action == 'create_workflow':
            params['name'] = match.group(1).strip()
            # Extract trigger type
            if 'new contact' in command or 'new lead' in command:
                params['trigger_type'] = 'new_contact'
            elif 'new deal' in command:
                params['trigger_type'] = 'new_deal'
            elif 'email' in command:
                params['trigger_type'] = 'email_received'
            else:
                params['trigger_type'] = 'manual'
            
            # Extract action type
            if 'send email' in command:
                params['action_type'] = 'send_email'
            elif 'create deal' in command:
                params['action_type'] = 'create_deal'
            elif 'assign' in command:
                params['action_type'] = 'assign_task'
            else:
                params['action_type'] = 'generic'
        
        elif action == 'delete_workflow':
            params['workflow_name'] = match.group(1).strip()
        
        elif action == 'update_workflow':
            params['workflow_name'] = match.group(1).strip()
            params['update_data'] = match.group(2).strip()
        
        elif action == 'trigger_workflow':
            params['workflow_name'] = match.group(1).strip()
            params['target'] = match.group(2).strip()
        
        elif action == 'search_contacts':
            params['criteria'] = match.group(1).strip()
        
        elif action == 'get_contact':
            params['contact_identifier'] = match.group(1).strip()
        
        return params
