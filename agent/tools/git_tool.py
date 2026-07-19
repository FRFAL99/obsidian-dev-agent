"""
Git operations tool - uso interno (non esposto all'LLM in chat, vedi tool_registry.HIDDEN_TOOLS)
"""

import os
import logging
import subprocess
from typing import Dict, Any

from agent.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class GitTool(BaseTool):
    name = "git"
    description = "Esegue operazioni Git (status, log, diff, commit, push) su una directory specifica"
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Sottocomando git da eseguire, es. 'status' o 'log --oneline -5'"},
            "cwd": {"type": "string", "description": "Directory di lavoro (repo) su cui eseguire il comando"},
        },
        "required": ["command", "cwd"],
    }

    def execute(self, command: str, cwd: str) -> Dict[str, Any]:
        try:
            env = {
                **os.environ,
                'GIT_AUTHOR_NAME': 'Documentation Agent',
                'GIT_AUTHOR_EMAIL': 'agent@local',
                'GIT_COMMITTER_NAME': 'Documentation Agent',
                'GIT_COMMITTER_EMAIL': 'agent@local',
            }

            result = subprocess.run(
                ['git'] + command.split(),
                cwd=cwd,
                capture_output=True,
                text=True,
                env=env,
            )

            return {
                'status': 'success',
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode,
            }
        except Exception as e:
            logger.error(f"Git command failed: {str(e)}")
            return {
                'status': 'error',
                'output': '',
                'error': str(e),
                'returncode': -1,
            }
