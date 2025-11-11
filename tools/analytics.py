"""
Analytics Tool
Track and analyze booking patterns and user behavior
"""

from typing import Dict
from data.db_manager import DatabaseManager

class AnalyticsTool:
    def __init__(self):
        self.db = DatabaseManager()
    
    def execute(self, args: Dict = None) -> Dict:
        """
        Get booking analytics and insights
        
        Args:
            query: str (optional - natural language query like "Italian restaurants")
            cuisine: str (optional - filter by cuisine type)
            location: str (optional - filter by location)
            restaurant_id: int (optional - get stats for specific restaurant)
            date_from: str (optional - start date for analytics)
            date_to: str (optional - end date for analytics)
        
        Returns:
            Dict with analytics data
        """
        try:
            # If no args provided, return general analytics
            if not args:
                analytics = self.db.get_analytics()
                return {
                    "success": True,
                    "analytics": analytics,
                    "message": "General analytics retrieved successfully"
                }
            
            # Check if user wants specific restaurant stats
            if 'restaurant_id' in args:
                return self.get_restaurant_stats(args)
            
            # Build filters for analytics query
            filters = {}
            if args.get('cuisine'):
                filters['cuisine'] = args['cuisine']
            if args.get('location'):
                filters['location'] = args['location']
            
            # Get filtered analytics
            analytics = self.db.get_analytics()
            
            # If filters provided, filter the results
            if filters:
                # Filter popular restaurants by cuisine/location
                if 'popular_restaurants' in analytics:
                    filtered_restaurants = []
                    for restaurant in analytics['popular_restaurants']:
                        match = True
                        if 'cuisine' in filters and restaurant.get('cuisine') != filters['cuisine']:
                            match = False
                        if 'location' in filters and restaurant.get('location') != filters['location']:
                            match = False
                        if match:
                            filtered_restaurants.append(restaurant)
                    analytics['popular_restaurants'] = filtered_restaurants
                
                # Add filter info to response
                analytics['filters_applied'] = filters
                message = f"Analytics for {filters.get('cuisine', '')} {filters.get('location', '')} restaurants".strip()
            else:
                message = "General analytics retrieved successfully"
            
            return {
                "success": True,
                "analytics": analytics,
                "filters": filters if filters else None,
                "message": message
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error retrieving analytics: {str(e)}"
            }
    
    def get_restaurant_stats(self, args: Dict) -> Dict:
        """
        Get statistics for a specific restaurant
        
        Args:
            restaurant_id: int
        """
        try:
            restaurant_id = int(args.get('restaurant_id'))
            
            restaurant = self.db.get_restaurant_by_id(restaurant_id)
            if not restaurant:
                return {"success": False, "error": "Restaurant not found"}
            
            # This would be expanded with more detailed stats
            return {
                "success": True,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant['name'],
                "rating": restaurant['rating'],
                "capacity": restaurant['capacity']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error retrieving restaurant stats: {str(e)}"
            }
