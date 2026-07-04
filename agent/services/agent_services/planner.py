"""
Planner service for AI Software Engineer agent
"""

from typing import Dict, Any, List
import logging
from ..tools.agent_tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class Planner:
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        self.tools = self._load_registered_tools()
        
    def _load_registered_tools(self) -> Dict[str, BaseTool]:
        """Load registered tools from the registry"""
        from ..tool_registry import ToolRegistry
        return ToolRegistry.get_registered_tools()
    
    def generate_plan(self, user_request: str) -> List[Dict]:
        """Generate step-by-step execution plan using LLM"""
        logger.info(f"Generating plan for request: {user_request}")
        
        # Initialize LLM if not already done
        if not hasattr(self, 'llm'):
            from ..llm import LLM
            self.llm = LLM()
        
        # Generate plan using LLM
        prompt = f"Based on the request: '{user_request}', generate a step-by-step plan using the available tools: {self.tools}"
        plan = self.llm.generate(prompt)
        
        return plan
    
    def _matches_request(self, tool: BaseTool, request: str) -> bool:
        """Check if tool is relevant to the request"""
        return request.lower() in tool.description.lower()
    
    def _suggest_parameters(self, tool: BaseTool, request: str) -> Dict:
        """Suggest parameters based on request"""
        return {
            'request': request,
            'context': self.context
        }