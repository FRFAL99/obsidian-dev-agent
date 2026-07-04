"""
Base capability class for AI Software Engineer agent
"""

from typing import Dict, Any, List
import logging
from ..services.agent_services.planner import Planner
from ..services.agent_services.executor import Executor

logger = logging.getLogger(__name__)

class BaseCapability:
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.planner = Planner(context)
        self.executor = Executor(context)
        
    def plan(self, user_request: str) -> List[Dict]:
        """Generate step-by-step plan for the request"""
        return self.planner.generate_plan(user_request)
    
    def execute(self, plan: List[Dict]) -> Dict:
        """Execute the generated plan"""
        return self.executor.execute_plan(plan)
    
    def _validate_plan(self, plan: List[Dict]) -> bool:
        """Basic plan validation"""
        if not plan:
            logger.error("Empty plan generated")
            return False
            
        for step in plan:
            if 'action' not in step:
                logger.error(f"Invalid step format: {step}")
                return False
                
        return True