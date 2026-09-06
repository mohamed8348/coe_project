import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BugIngestionPipeline:
    VALID_MODULES = {'Finance', 'HR', 'Payroll', 'Procurement', 'Inventory', 'Manufacturing', 'CRM', 'Sales', 'Compliance'}
    
    def ingest(self, bug_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates required fields, fills missing optional fields with defaults,
        and returns a normalized bug dictionary.
        """
        logger.info(f"Ingesting bug: {bug_dict.get('bug_id', 'UNKNOWN')}")
        
        required_fields = ['bug_id', 'title', 'description', 'module']
        for field in required_fields:
            if field not in bug_dict or not bug_dict[field]:
                raise ValueError(f"Missing required field: {field}")
                
        module = bug_dict['module']
        if module not in self.VALID_MODULES:
            raise ValueError(f"Invalid module '{module}'. Must be one of: {', '.join(self.VALID_MODULES)}")
            
        normalized_bug = bug_dict.copy()
        
        # Fill optional fields with defaults
        normalized_bug.setdefault('log_content', '')
        normalized_bug.setdefault('log_content_clean', '')
        normalized_bug.setdefault('screenshot_meta', {})
        normalized_bug.setdefault('severity', 'Medium')
        normalized_bug.setdefault('fix_category', 'Unknown')
        
        logger.info(f"Successfully ingested bug {normalized_bug['bug_id']}")
        return normalized_bug
