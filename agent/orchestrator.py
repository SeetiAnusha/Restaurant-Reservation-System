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

from agent.prompt_manager_v6 import get_system_prompt
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
        system_prompt = get_system_prompt("v6")
        self.context_manager.add_message("system", system_prompt)
    
    def process_message(self, user_message: str, user_name: str = "Guest", user_id: Optional[int] = None) -> str:
        """
        Process user message and return response
        
        Args:
            user_message: User's input message
            user_name: User's name for personalization
            user_id: User's database ID for linking reservations
        
        Returns:
            Assistant's response
        """
        # Store user name and ID in context
        self.context_manager.set_user_context("user_name", user_name)
        print("user_name:",user_name);
        if user_id:
            self.context_manager.set_user_context("user_id", user_id)
        
        # Add user message to history
        self.context_manager.add_message("user", user_message)
        
        # Get LLM response
        assistant_response = self._get_llm_response()
        print("\n" + "="*70)
        print("🤖 LLM RAW RESPONSE:")
        print("="*70)
        print(assistant_response)
        print("="*70 + "\n")
        
        # Check if response contains tool calls
        tool_calls = self._extract_tool_calls(assistant_response)
        print("🔧 EXTRACTED TOOL CALLS:", tool_calls)
        
        if tool_calls:
            # Don't show the tool call response to user - it's internal processing
            # Execute tools and get results
            tool_results = self._execute_tools(tool_calls)            
            print("tool_results:",tool_results)


            
            
            # Add tool results to context and get final response
            tool_results_text = self._format_tool_results(tool_results)
            print("tool_results_text:",tool_results_text)

            self.context_manager.add_message("system", f"Tool Results:\n{tool_results_text}")
            
            
            # Determine what kind of response to give based on tool results
            last_tool = tool_results[-1] if tool_results else None
            
            if last_tool and last_tool['function'] == 'book_reservation':
                # Booking was just made
                instruction = (
                    "CRITICAL: You just called book_reservation tool and received the result above. "
                    "Tell the user their booking is CONFIRMED. Include: "
                    "1. Restaurant name, 2. Date and time, 3. Party size, 4. Confirmation code. "
                    "Use a friendly tone with emoji like ✅. "
                    "Example: '✅ Booked! Your table for 4 at GoodFoods - Indian - JP Nagar is confirmed for today at 7pm. Confirmation code: GF-0043' "
                    "Do NOT call any more tools. Do NOT include XML tags."
                )
            elif last_tool and last_tool['function'] == 'recommend_restaurants':
                # Restaurants were found
                instruction = (
                    "CRITICAL: You just searched for restaurants and received results above. "
                    "Show the user the available restaurants with their details (name, location, rating, available seats). "
                    "If user asked to book, ask which restaurant they want to book. "
                    "If they just asked for recommendations, present the options nicely. "
                    "Do NOT call any more tools. Do NOT include XML tags. Do NOT say 'booking confirmed' yet."
                )
            else:
                # Other tools
                instruction = (
                    "CRITICAL: You have received tool results above. Do NOT call any more tools. "
                    "Respond to the user in natural language using ONLY the information from the tool results. "
                    "Do NOT include any XML tags or tool calls in your response."
                )
            
            self.context_manager.add_message("system", instruction)
            
            # Get final response incorporating tool results
            final_response = self._get_llm_response()
            # print("final_response:",final_response)
            
            # Check if LLM is STILL trying to call tools (it shouldn't!)
            max_retries = 2
            retry_count = 0
            
            while "<tool_call>" in final_response and retry_count < max_retries:
                print(f"WARNING: LLM tried to call tools in final response (attempt {retry_count + 1}). Stripping and retrying...")
                
                # Strip tool calls first
                cleaned_response = self._strip_tool_calls_from_text(final_response)
                
                # If response is now empty or too short after stripping, ask LLM again
                if len(cleaned_response.strip()) < 20:
                    self.context_manager.add_message("system", 
                        f"ERROR: You must respond in plain text only. "
                        f"Look at the tool results above and tell the user what happened. "
                        f"If there was an error, explain it. If it was successful, confirm it. "
                        f"NO <tool_call> TAGS. Just write a normal sentence.")
                    final_response = self._get_llm_response()
                    retry_count += 1
                else:
                    final_response = cleaned_response
                    break
            
            # Final cleanup: strip any remaining XML
            final_response = self._strip_tool_calls_from_text(final_response)
            
            # Also strip any "Tool Results:" text that might leak through
            if "Tool Results:" in final_response:
                final_response = final_response.split("Tool Results:")[0].strip()
            
            # Clean up any garbage characters at the start
            final_response = final_response.strip()
            
            # Remove any leading garbage before actual text (look for first capital letter followed by lowercase)
            import re
            match = re.search(r'[A-Z][a-z]', final_response)
            if match and match.start() > 10:
                # There's garbage before the actual text, remove it
                final_response = final_response[match.start():]
            
            print("final_response:",final_response)
            
            # If still empty after all this, create a fallback response from tool results
            if len(final_response.strip()) < 10:
                final_response = self._create_fallback_response(tool_results)
                print(f"⚠️ Using fallback response: {final_response}")
            
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
        
        print(f"🔍 Regex found {len(matches)} tool call(s) in response")
        
        for function_name, args_str in matches:
            function_name = function_name.strip()
            print(f"   - Function: {function_name}")
            print(f"   - Args (raw): {args_str.strip()[:100]}...")
            try:
                # Parse JSON args
                args = json.loads(args_str.strip())
                tool_calls.append({
                    "function": function_name,
                    "args": args
                })
                print(f"   ✅ Successfully parsed args")
            except json.JSONDecodeError as e:
                # Try to extract args manually if JSON parsing fails
                print(f"   ❌ Could not parse args for {function_name}: {e}")
                continue
        
        return tool_calls
    
    def _strip_tool_calls_from_text(self, response: str) -> str:
        """Remove tool call XML from response text"""
        # Remove all <tool_call>...</tool_call> blocks
        pattern = r'<tool_call>.*?</tool_call>'
        cleaned = re.sub(pattern, '', response, flags=re.DOTALL)
        return cleaned.strip()
    
    def _create_fallback_response(self, tool_results: List[Dict]) -> str:
        """Create a user-friendly response from tool results when LLM fails"""
        if not tool_results:
            return "I've processed your request. Please let me know if you need any additional information."
        
        # Get the last tool result (most recent)
        result = tool_results[-1]
        function_name = result.get('function', '')
        result_data = result.get('result', {})
        
        # Handle different function types
        if function_name == 'book_reservation':
            if result_data.get('success'):
                restaurant_name = result_data.get('restaurant_name', 'the restaurant')
                date = result_data.get('date', '')
                time = result_data.get('time', '')
                party_size = result_data.get('party_size', '')
                confirmation = result_data.get('confirmation_code', result_data.get('reservation_id', ''))
                return f"✅ Booked! Your table for {party_size} at {restaurant_name} is confirmed for {date} at {time}. Confirmation code: {confirmation}"
            else:
                error = result_data.get('error', 'Unknown error')
                return f"I couldn't complete the booking: {error}. Would you like to try a different time or restaurant?"
        
        elif function_name == 'recommend_restaurants':
            recommendations = result_data.get('recommendations', [])
            if recommendations:
                count = len(recommendations)
                first = recommendations[0]
                return f"I found {count} available restaurants! The top option is {first.get('name')} in {first.get('location')} with {first.get('rating')} rating. Would you like to book it?"
            else:
                return "I couldn't find any restaurants matching your criteria. Would you like to try different search parameters?"
        
        elif function_name == 'get_user_reservations':
            reservations = result_data.get('reservations', [])
            if reservations:
                return f"You have {len(reservations)} reservation(s). Let me know if you'd like to modify or cancel any of them."
            else:
                return "You don't have any reservations at the moment. Would you like to make one?"
        
        # Default fallback
        return "I've processed your request. Please let me know if you need any additional information."
    
    def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute tool calls and return results"""
        results = []
        
        for tool_call in tool_calls:
            function_name = tool_call["function"]
            args = tool_call["args"]
            
            # Add user_name and user_id to args if needed
            if function_name in ["book_reservation", "get_user_reservations"]:
                if "user_name" not in args:
                    args["user_name"] = self.context_manager.get_user_context("user_name", "Guest")
                    print(f"✅ Auto-added user_name: '{args['user_name']}'")
                else:
                    print(f"⚠️ LLM provided user_name: '{args['user_name']}' (should be auto-added!)")
                if "user_id" not in args:
                    user_id = self.context_manager.get_user_context("user_id")
                    if user_id:
                        args["user_id"] = user_id
                        print(f"✅ Auto-added user_id: {user_id}")
            
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
        if "date" in args and args["date"] is not None:
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
        if "time" in args and args["time"] is not None:
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
        system_prompt = get_system_prompt("v6")
        self.context_manager.add_message("system", system_prompt)
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.context_manager.get_history(include_system=False)
