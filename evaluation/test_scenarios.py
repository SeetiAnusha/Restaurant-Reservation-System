"""
Test Scenarios and Evaluation Framework
Automated testing of conversation flows
"""

import json
from typing import List, Dict
from datetime import datetime, timedelta

# Test scenarios covering different user journeys
TEST_SCENARIOS = [
    {
        "name": "Simple Booking - Happy Path",
        "conversation": [
            {
                "user": "I want to book a table for 4 tomorrow at 7pm, Italian food",
                "expected_tools": ["recommend_restaurants"],
                "expected_intent": "book"
            },
            {
                "user": "The first one looks good",
                "expected_tools": ["book_reservation"],
                "expected_intent": "book"
            }
        ],
        "success_criteria": {
            "booking_created": True,
            "confirmation_code_provided": True
        }
    },
    {
        "name": "Recommendation Only",
        "conversation": [
            {
                "user": "What are some good Chinese restaurants in New York?",
                "expected_tools": ["recommend_restaurants"],
                "expected_intent": "recommend"
            }
        ],
        "success_criteria": {
            "recommendations_provided": True,
            "min_recommendations": 3
        }
    },
    {
        "name": "Fully Booked - Alternative Times",
        "conversation": [
            {
                "user": "Book me at the busiest restaurant tonight at 8pm for 2",
                "expected_tools": ["recommend_restaurants", "check_availability"],
                "expected_intent": "book"
            }
        ],
        "success_criteria": {
            "alternatives_offered": True
        }
    },
    {
        "name": "View Reservations",
        "conversation": [
            {
                "user": "Show me my reservations",
                "expected_tools": ["get_user_reservations"],
                "expected_intent": "view"
            }
        ],
        "success_criteria": {
            "reservations_listed": True
        }
    },
    {
        "name": "Cancel Reservation",
        "conversation": [
            {
                "user": "I need to cancel my reservation",
                "expected_tools": ["get_user_reservations"],
                "expected_intent": "cancel"
            },
            {
                "user": "Cancel the first one",
                "expected_tools": ["cancel_reservation"],
                "expected_intent": "cancel"
            }
        ],
        "success_criteria": {
            "cancellation_confirmed": True
        }
    },
    {
        "name": "Multi-Turn Clarification",
        "conversation": [
            {
                "user": "I want to book a table",
                "expected_tools": [],
                "expected_intent": "book"
            },
            {
                "user": "For 4 people",
                "expected_tools": [],
                "expected_intent": "book"
            },
            {
                "user": "Tomorrow at 7pm",
                "expected_tools": [],
                "expected_intent": "book"
            },
            {
                "user": "Italian food",
                "expected_tools": ["recommend_restaurants"],
                "expected_intent": "book"
            }
        ],
        "success_criteria": {
            "gathered_all_info": True,
            "recommendations_provided": True
        }
    },
    {
        "name": "Specific Restaurant by Name",
        "conversation": [
            {
                "user": "Do you have availability at Bella Notte tomorrow at 8pm for 2?",
                "expected_tools": ["recommend_restaurants", "check_availability"],
                "expected_intent": "info"
            }
        ],
        "success_criteria": {
            "availability_checked": True
        }
    },
    {
        "name": "Large Party",
        "conversation": [
            {
                "user": "I need to book for 15 people next Friday",
                "expected_tools": [],
                "expected_intent": "book"
            }
        ],
        "success_criteria": {
            "large_party_handled": True,
            "special_instructions_mentioned": True
        }
    },
    {
        "name": "Dietary Restrictions",
        "conversation": [
            {
                "user": "Find me restaurants with vegan options for tomorrow lunch",
                "expected_tools": ["recommend_restaurants"],
                "expected_intent": "recommend"
            }
        ],
        "success_criteria": {
            "dietary_filter_applied": True,
            "recommendations_provided": True
        }
    },
    {
        "name": "Price Range Filter",
        "conversation": [
            {
                "user": "Show me affordable restaurants, nothing too expensive",
                "expected_tools": ["recommend_restaurants"],
                "expected_intent": "recommend"
            }
        ],
        "success_criteria": {
            "price_filter_applied": True,
            "recommendations_provided": True
        }
    }
]

class ConversationEvaluator:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.results = []
    
    def run_scenario(self, scenario: Dict) -> Dict:
        """Run a single test scenario"""
        print(f"\n{'='*60}")
        print(f"Testing: {scenario['name']}")
        print(f"{'='*60}")
        
        # Reset conversation
        self.orchestrator.reset_conversation()
        
        scenario_result = {
            "name": scenario['name'],
            "passed": True,
            "turns": [],
            "errors": []
        }
        
        for i, turn in enumerate(scenario['conversation'], 1):
            print(f"\nTurn {i}:")
            print(f"User: {turn['user']}")
            
            try:
                response = self.orchestrator.process_message(turn['user'], "TestUser")
                print(f"Assistant: {response[:200]}...")
                
                turn_result = {
                    "user_message": turn['user'],
                    "assistant_response": response,
                    "expected_tools": turn.get('expected_tools', []),
                    "expected_intent": turn.get('expected_intent', ''),
                    "success": True
                }
                
                scenario_result['turns'].append(turn_result)
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                scenario_result['passed'] = False
                scenario_result['errors'].append(f"Turn {i}: {str(e)}")
                turn_result = {
                    "user_message": turn['user'],
                    "error": str(e),
                    "success": False
                }
                scenario_result['turns'].append(turn_result)
        
        # Check success criteria
        self._check_success_criteria(scenario_result, scenario.get('success_criteria', {}))
        
        status = "✅ PASSED" if scenario_result['passed'] else "❌ FAILED"
        print(f"\n{status}")
        
        return scenario_result
    
    def _check_success_criteria(self, result: Dict, criteria: Dict):
        """Check if success criteria are met"""
        # This is a simplified check - in production would be more sophisticated
        if criteria.get('booking_created'):
            # Check if any turn mentions confirmation
            has_confirmation = any('confirmation' in turn.get('assistant_response', '').lower() 
                                  for turn in result['turns'])
            if not has_confirmation:
                result['passed'] = False
                result['errors'].append("No booking confirmation found")
        
        if criteria.get('recommendations_provided'):
            # Check if recommendations were given
            has_recommendations = any('restaurant' in turn.get('assistant_response', '').lower() 
                                     for turn in result['turns'])
            if not has_recommendations:
                result['passed'] = False
                result['errors'].append("No recommendations provided")
    
    def run_all_scenarios(self) -> Dict:
        """Run all test scenarios"""
        print("\n" + "="*60)
        print("STARTING EVALUATION")
        print("="*60)
        
        for scenario in TEST_SCENARIOS:
            result = self.run_scenario(scenario)
            self.results.append(result)
        
        # Calculate metrics
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        summary = {
            "total_scenarios": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "results": self.results
        }
        
        self._print_summary(summary)
        
        return summary
    
    def _print_summary(self, summary: Dict):
        """Print evaluation summary"""
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Scenarios: {summary['total_scenarios']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print("="*60)
        
        if summary['failed'] > 0:
            print("\nFailed Scenarios:")
            for result in summary['results']:
                if not result['passed']:
                    print(f"  ❌ {result['name']}")
                    for error in result['errors']:
                        print(f"     - {error}")
    
    def save_results(self, filename: str = "evaluation_results.json"):
        """Save results to file"""
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.results
            }, f, indent=2)
        print(f"\n📄 Results saved to {filename}")

def main():
    """Main evaluation function"""
    import os
    from dotenv import load_dotenv
    from agent.orchestrator import AgentOrchestrator
    
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return
    
    print("🚀 Initializing agent...")
    orchestrator = AgentOrchestrator(api_key)
    
    print("🧪 Starting evaluation...")
    evaluator = ConversationEvaluator(orchestrator)
    summary = evaluator.run_all_scenarios()
    
    # Save results
    evaluator.save_results()
    
    print("\n✨ Evaluation complete!")

if __name__ == "__main__":
    main()
