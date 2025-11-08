"""
Context Manager
Manages conversation history and context window
"""

from typing import List, Dict
from datetime import datetime

class ContextManager:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.conversation_history = []
        self.user_context = {}
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history:
            # Keep system message and recent messages
            self.conversation_history = [self.conversation_history[0]] + \
                                       self.conversation_history[-(self.max_history-1):]
    
    def get_history(self, include_system: bool = True) -> List[Dict]:
        """Get conversation history for LLM"""
        if include_system:
            return [{"role": msg["role"], "content": msg["content"]} 
                   for msg in self.conversation_history]
        else:
            return [{"role": msg["role"], "content": msg["content"]} 
                   for msg in self.conversation_history 
                   if msg["role"] != "system"]
    
    def set_user_context(self, key: str, value: any):
        """Store user context information"""
        self.user_context[key] = value
    
    def get_user_context(self, key: str, default=None):
        """Retrieve user context information"""
        return self.user_context.get(key, default)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.user_context = {}
    
    def get_recent_context(self, n: int = 5) -> str:
        """Get summary of recent conversation"""
        recent = self.conversation_history[-n:]
        summary = []
        for msg in recent:
            if msg["role"] == "user":
                summary.append(f"User: {msg['content'][:100]}")
            elif msg["role"] == "assistant":
                summary.append(f"Assistant: {msg['content'][:100]}")
        return "\n".join(summary)
