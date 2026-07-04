"""
Memory Engine for AI Agent
Handles persistent memory storage and context-aware data retention
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MemoryEngine:
    def __init__(self, memory_file: str = "agent_memory.json", context_window: int = 10):
        """
        Initialize memory engine
        
        Args:
            memory_file: Path to persistent memory storage
            context_window: Maximum number of recent memories to retain
        """
        self.memory_file = memory_file
        self.context_window = context_window
        self.in_memory = {}
        self._load_persistent_memory()
        
    def _load_persistent_memory(self):
        """Load memory from persistent storage"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    self.in_memory = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load persistent memory: {str(e)}")
    
    def _save_persistent_memory(self):
        """Save memory to persistent storage"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.in_memory, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save persistent memory: {str(e)}")
    
    def store_memory(self, key: str, value: Any, context: Optional[Dict] = None):
        """
        Store a memory entry
        
        Args:
            key: Unique identifier for the memory
            value: Data to store
            context: Additional context information
        """
        try:
            self.in_memory[key] = {
                "value": value,
                "context": context or {},
                "timestamp": datetime.datetime.now().isoformat()
            }
            self._save_persistent_memory()
        except Exception as e:
            logger.error(f"Memory store failed: {str(e)}")
    
    def get_memory(self, key: str) -> Optional[Dict]:
        """
        Retrieve a memory entry by key
        
        Args:
            key: Unique identifier for the memory
            
        Returns:
            Dictionary containing memory data or None if not found
        """
        return self.in_memory.get(key)
    
    def get_contextual_memories(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve memories in chronological order with context awareness
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of memory entries ordered by timestamp
        """
        # Sort memories by timestamp
        sorted_memories = sorted(
            self.in_memory.values(),
            key=lambda x: x['timestamp']
        )
        
        # Return latest 'limit' memories
        return sorted_memories[-limit:]
    
    def clean_old_memories(self, max_age_seconds: int = 86400):
        """
        Remove memories older than a specified time threshold
        
        Args:
            max_age_seconds: Maximum age in seconds for memories to retain
        """
        current_time = datetime.datetime.now()
        to_remove = []
        
        for key, memory in self.in_memory.items():
            try:
                timestamp = datetime.datetime.fromisoformat(memory['timestamp'])
                if (current_time - timestamp).total_seconds() > max_age_seconds:
                    to_remove.append(key)
            except Exception as e:
                logger.warning(f"Failed to process memory timestamp: {str(e)}")
        
        for key in to_remove:
            del self.in_memory[key]
            logger.info(f"Removed old memory: {key}")
        
        self._save_persistent_memory()
