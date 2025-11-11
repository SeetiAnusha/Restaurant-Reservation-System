"""
Availability Tool
Check restaurant availability for specific date/time/party size
"""

from typing import Dict
from data.db_manager import DatabaseManager

class AvailabilityTool:
    def __init__(self):
        self.db = DatabaseManager()
    
    def execute(self, args: Dict) -> Dict:
        """
        Check availability for a restaurant
        
        Args:
            restaurant_id: int
            date: str (YYYY-MM-DD format)
            time: str (HH:MM format)
            party_size: int
        
        Returns:
            Dict with availability status and details
        """
        try:
            # Validate that wrong arguments aren't passed
            if 'query' in args or 'cuisine' in args or 'location' in args:
                return {
                    "success": False,
                    "error": "Wrong tool! Use 'recommend_restaurants' to search by name/location/cuisine. This tool only checks availability for a specific restaurant ID."
                }
            
            # Get restaurant_id
            restaurant_id_raw = args.get('restaurant_id')
            
            if restaurant_id_raw is None:
                return {
                    "success": False,
                    "error": "Missing restaurant_id. Use 'recommend_restaurants' first to find the restaurant and get its ID."
                }
            
            # Try to convert to int
            try:
                restaurant_id = int(restaurant_id_raw)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "error": f"Invalid restaurant_id: '{restaurant_id_raw}'. Must be a NUMBER (e.g., 123), not a name. Use 'recommend_restaurants' to search by name."
                }
            
            date = args.get('date')
            time = args.get('time')
            party_size_raw = args.get('party_size')
            
            if party_size_raw is None:
                return {
                    "success": False,
                    "error": "Missing party_size parameter"
                }
            
            party_size = int(party_size_raw)
            
            # Validate inputs
            if not all([restaurant_id, date, time, party_size]):
                return {
                    "success": False,
                    "error": "Missing required parameters"
                }
            
            # Get restaurant details
            restaurant = self.db.get_restaurant_by_id(restaurant_id)
            if not restaurant:
                return {
                    "success": False,
                    "error": f"Restaurant with ID {restaurant_id} not found"
                }
            
            # Check availability
            availability = self.db.check_availability(restaurant_id, date, time, party_size)
            
            result = {
                "success": True,
                "restaurant_name": restaurant['name'],
                "restaurant_id": restaurant_id,
                "date": date,
                "time": time,
                "party_size": party_size,
                "available": availability['available']
            }
            
            if availability['available']:
                result['seats_available'] = availability['seats_available']
                result['message'] = f"✅ {restaurant['name']} has availability for {party_size} guests"
            else:
                result['reason'] = availability['reason']
                result['message'] = f"❌ {restaurant['name']} is not available: {availability['reason']}"
                
                # Suggest alternative times
                alternative_times = self.db.get_available_times(restaurant_id, date, party_size)
                if alternative_times:
                    result['alternative_times'] = alternative_times[:5]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error checking availability: {str(e)}"
            }
    
    def get_available_times(self, args: Dict) -> Dict:
        """
        Get all available time slots for a restaurant on a date
        
        Args:
            restaurant_id: int
            date: str (YYYY-MM-DD format)
            party_size: int
        """
        try:
            restaurant_id = int(args.get('restaurant_id'))
            date = args.get('date')
            party_size = int(args.get('party_size'))
            
            restaurant = self.db.get_restaurant_by_id(restaurant_id)
            if not restaurant:
                return {"success": False, "error": "Restaurant not found"}
            
            available_times = self.db.get_available_times(restaurant_id, date, party_size)
            
            return {
                "success": True,
                "restaurant_name": restaurant['name'],
                "date": date,
                "party_size": party_size,
                "available_times": available_times,
                "count": len(available_times)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting available times: {str(e)}"
            }
