"""
Agent Orchestrator
Main agent loop with tool routing and LLM integration
"""

import os
import re
import json
from typing import Dict, List, Optional
from groq import Groq
from datetime import datetime, timedelta

from agent.prompt_manager import get_system_prompt
from agent.context_manager import ContextManager
from tools.recommendations import RecommendationTool
from tools.availability import AvailabilityTool
from tools.booking import BookingTool
from tools.analytics import AnalyticsTool

class AgentOrchestrator:
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.context_manager = ContextManager()
        
        # Initialize tools
        self.tools = {
            "recommend_restaurants": RecommendationTool(),
            "check_availability": AvailabilityTool(),
            "book_reservation": BookingTool(),
            "cancel_reservation": BookingTool(),
            "get_user_reservations": BookingTool(),
            "get_analytics": AnalyticsTool()
        }
        
        # Add system prompt to context
        system_prompt = get_system_prompt("v4")
        self.context_manager.add_message("system", system_prompt)
    
    def process_message(self, user_message: str, user_name: str = "Guest") -> str:
        """
        Process user message and return response
        
        Args:
            user_message: User's input message
            user_name: User's name for personalization
        
        Returns:
            Assistant's response
        """
        # Store user name in context
        self.context_manager.set_user_context("user_name", user_name)
        
        # Add user message to history
        self.context_manager.add_message("user", user_message)
        
        # Get LLM response
        assistant_response = self._get_llm_response()
        
        # Check if response contains tool calls
        tool_calls = self._extract_tool_calls(assistant_response)
        
        if tool_calls:
            # Execute tools and get results
            tool_results = self._execute_tools(tool_calls)
            
            # Add tool results to context and get final response
            tool_results_text = self._format_tool_results(tool_results)
            self.context_manager.add_message("system", f"Tool Results:\n{tool_results_text}")
            
            # Get final response incorporating tool results
            final_response = self._get_llm_response()
            self.context_manager.add_message("assistant", final_response)
            
            return final_response
        else:
            # No tools needed, return response directly
            self.context_manager.add_message("assistant", assistant_response)
            return assistant_response
    
    def _get_llm_response(self) -> str:
        """Get response from LLM"""
        try:
            messages = self.context_manager.get_history()
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def _extract_tool_calls(self, response: str) -> List[Dict]:
        """Extract tool calls from LLM response using XML parsing"""
        tool_calls = []
        
        # Pattern to match <tool_call>...</tool_call>
        pattern = r'<tool_call>\s*<function>(.*?)</function>\s*<args>(.*?)</args>\s*</tool_call>'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for function_name, args_str in matches:
            function_name = function_name.strip()
            try:
                # Parse JSON args
                args = json.loads(args_str.strip())
                tool_calls.append({
                    "function": function_name,
                    "args": args
                })
            except json.JSONDecodeError:
                # Try to extract args manually if JSON parsing fails
                print(f"Warning: Could not parse args for {function_name}")
                continue
        
        return tool_calls
    
    def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute tool calls and return results"""
        results = []
        
        for tool_call in tool_calls:
            function_name = tool_call["function"]
            args = tool_call["args"]
            
            # Add user_name to args if needed
            if function_name in ["book_reservation", "get_user_reservations"]:
                if "user_name" not in args:
                    args["user_name"] = self.context_manager.get_user_context("user_name", "Guest")
            
            # Handle date/time parsing
            args = self._parse_temporal_args(args)
            
            # Execute tool
            if function_name in self.tools:
                tool = self.tools[function_name]
                
                # Route to correct method
                if function_name == "cancel_reservation":
                    result = tool.cancel(args)
                elif function_name == "get_user_reservations":
                    result = tool.get_user_reservations(args)
                else:
                    result = tool.execute(args)
                
                results.append({
                    "function": function_name,
                    "args": args,
                    "result": result
                })
            else:
                results.append({
                    "function": function_name,
                    "args": args,
                    "result": {"success": False, "error": f"Unknown tool: {function_name}"}
                })
        
        return results
    
    def _parse_temporal_args(self, args: Dict) -> Dict:
        """Parse and normalize date/time arguments"""
        # Handle relative dates like "tomorrow", "today"
        if "date" in args:
            date_str = args["date"].lower()
            
            if date_str == "today":
                args["date"] = datetime.now().strftime("%Y-%m-%d")
            elif date_str == "tomorrow":
                args["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            elif "next" in date_str:
                # Handle "next friday", etc.
                # Simplified - in production would use dateparser library
                args["date"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Normalize time format
        if "time" in args:
            time_str = args["time"]
            # Convert "7pm" to "19:00"
            if "pm" in time_str.lower() or "am" in time_str.lower():
                time_str = time_str.lower().replace(" ", "")
                if "pm" in time_str:
                    hour = int(time_str.replace("pm", "").split(":")[0])
                    if hour != 12:
                        hour += 12
                    args["time"] = f"{hour:02d}:00"
                else:
                    hour = int(time_str.replace("am", "").split(":")[0])
                    if hour == 12:
                        hour = 0
                    args["time"] = f"{hour:02d}:00"
        
        return args
    
    def _format_tool_results(self, results: List[Dict]) -> str:
        """Format tool results for LLM context"""
        formatted = []
        
        for result in results:
            formatted.append(f"Function: {result['function']}")
            formatted.append(f"Result: {json.dumps(result['result'], indent=2)}")
            formatted.append("---")
        
        return "\n".join(formatted)
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.context_manager.clear_history()
        system_prompt = get_system_prompt("v4")
        self.context_manager.add_message("system", system_prompt)
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.context_manager.get_history(include_system=False)
