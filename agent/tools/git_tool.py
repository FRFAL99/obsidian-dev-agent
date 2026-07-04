"""
Git operations tool for AI Software Engineer agent
"""

from typing import Dict, Any, List
import logging
import subprocess
from ..agent_tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class GitTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="git",
            description="Perform Git operations such as commit, push, pull, and status checks"
        )
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a Git command"""
        try:
            # Set up environment
            env = {
                **os.environ,
                'GIT_AUTHOR_NAME': 'AI Agent',
                'GIT_AUTHOR_EMAIL': 'agent@example.com',
                'GIT_COMMITTER_NAME': 'AI Agent',
                'GIT_COMMITTER_EMAIL': 'agent@example.com'
            }
            
            # Execute command
            result = subprocess.run(
                ['git'] + command.split(),
                capture_output=True,
                text=True,
                env=env,
                **kwargs
            )
            
            return {
                'status': 'success',
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            logger.error(f"Git command failed: {str(e)}")
            return {
                'status': 'error',
                'output': '',
                'error': str(e),
                'returncode': -1
            }