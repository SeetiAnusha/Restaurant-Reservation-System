"""
Booking Tool
Create, modify, and cancel reservations
"""

from typing import Dict
from data.db_manager import DatabaseManager

class BookingTool:
    def __init__(self):
        self.db = DatabaseManager()
    
    def execute(self, args: Dict) -> Dict:
        """
        Create a new reservation
        
        Args:
            restaurant_id: int
            user_name: str
            date: str (YYYY-MM-DD format)
            time: str (HH:MM format)
            party_size: int
            user_email: str (optional)
            special_requests: str (optional)
        
        Returns:
            Dict with reservation confirmation
        """
        try:
            restaurant_id = int(args.get('restaurant_id'))
            user_name = args.get('user_name')
            date = args.get('date')
            time = args.get('time')
            party_size = int(args.get('party_size'))
            user_email = args.get('user_email')
            special_requests = args.get('special_requests')
            
            # Validate required fields
            if not all([restaurant_id, user_name, date, time, party_size]):
                return {
                    "success": False,
                    "error": "Missing required fields"
                }
            
            # Create reservation
            result = self.db.create_reservation(
                restaurant_id=restaurant_id,
                user_name=user_name,
                date=date,
                time=time,
                party_size=party_size,
                user_email=user_email,
                special_requests=special_requests
            )
            
            if result['success']:
                message = f"🎉 Reservation confirmed!\n\n"
                message += f"📍 Restaurant: {result['restaurant_name']}\n"
                message += f"📅 Date: {result['date']}\n"
                message += f"🕐 Time: {result['time']}\n"
                message += f"👥 Party Size: {result['party_size']}\n"
                message += f"🎫 Confirmation Code: {result['confirmation_code']}"
                
                result['message'] = message
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating reservation: {str(e)}"
            }
    
    def cancel(self, args: Dict) -> Dict:
        """
        Cancel a reservation
        
        Args:
            reservation_id: int
        """
        try:
            reservation_id = int(args.get('reservation_id'))
            
            result = self.db.cancel_reservation(reservation_id)
            
            if result['success']:
                result['message'] = f"✅ Reservation #{reservation_id} has been cancelled successfully"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error cancelling reservation: {str(e)}"
            }
    
    def get_user_reservations(self, args: Dict) -> Dict:
        """
        Get all reservations for a user
        
        Args:
            user_name: str
        """
        try:
            user_name = args.get('user_name')
            
            if not user_name:
                return {"success": False, "error": "User name required"}
            
            reservations = self.db.get_user_reservations(user_name)
            
            formatted_reservations = []
            for res in reservations:
                formatted_reservations.append({
                    "reservation_id": res['id'],
                    "confirmation_code": f"GF-{res['id']:04d}",
                    "restaurant_name": res['restaurant_name'],
                    "location": res['location'],
                    "date": res['date'],
                    "time": res['time'],
                    "party_size": res['party_size'],
                    "special_requests": res['special_requests']
                })
            
            return {
                "success": True,
                "user_name": user_name,
                "count": len(formatted_reservations),
                "reservations": formatted_reservations
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error retrieving reservations: {str(e)}"
            }
