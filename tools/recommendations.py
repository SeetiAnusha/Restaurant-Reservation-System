"""
Recommendation Tool
Suggest restaurants based on user preferences using hybrid search
"""

from typing import Dict, List
import json
from data.db_manager import DatabaseManager
from data.embeddings import EmbeddingManager

class RecommendationTool:
    def __init__(self):
        self.db = DatabaseManager()
        self.embeddings = EmbeddingManager()
        self.embeddings.compute_embeddings()
    
    def execute(self, args: Dict) -> Dict:
        """
        Recommend restaurants based on preferences
        
        Args:
            query: str (natural language query, e.g., "romantic Italian place")
            cuisine: str (optional)
            location: str (optional)
            party_size: int (optional)
            min_rating: float (optional)
            price_range: str (optional, e.g., "$$")
            date: str (optional, for availability filtering)
            time: str (optional, for availability filtering)
        
        Returns:
            Dict with recommended restaurants
        """
        try:
            query = args.get('query', '')
            party_size = args.get('party_size')
            date = args.get('date')
            time = args.get('time')
            
            # Build filters
            filters = {}
            if args.get('cuisine'):
                filters['cuisine'] = args['cuisine']
            if args.get('location'):
                filters['location'] = args['location']
            if args.get('min_rating'):
                filters['min_rating'] = float(args['min_rating'])
            if args.get('price_range'):
                filters['price_range'] = args['price_range']
            
            # Get recommendations using hybrid search
            if query:
                recommendations = self.embeddings.hybrid_search(
                    query=query,
                    filters=filters if filters else None,
                    top_k=10
                )
            else:
                # Fallback to database query
                recommendations = self.db.get_restaurants(filters)
                # Sort by rating
                recommendations.sort(key=lambda x: x['rating'], reverse=True)
                recommendations = recommendations[:10]
            
            # Filter by availability if date/time provided
            if date and time and party_size:
                available_recommendations = []
                for restaurant in recommendations:
                    availability = self.db.check_availability(
                        restaurant['id'], date, time, int(party_size)
                    )
                    restaurant['available'] = availability['available']
                    if availability['available']:
                        restaurant['seats_available'] = availability['seats_available']
                        available_recommendations.append(restaurant)
                
                # Prioritize available restaurants
                recommendations = available_recommendations + [
                    r for r in recommendations if not r.get('available', False)
                ]
            
            # Format results
            formatted_results = []
            for i, restaurant in enumerate(recommendations[:5], 1):
                features = json.loads(restaurant['special_features'])
                
                result = {
                    "rank": i,
                    "id": restaurant['id'],
                    "name": restaurant['name'],
                    "cuisine": restaurant['cuisine'],
                    "location": restaurant['location'],
                    "rating": restaurant['rating'],
                    "price_range": restaurant['price_range'],
                    "capacity": restaurant['capacity'],
                    "features": features,
                    "description": restaurant['description']
                }
                
                if 'available' in restaurant:
                    result['available'] = restaurant['available']
                    if restaurant['available']:
                        result['seats_available'] = restaurant.get('seats_available', 0)
                
                formatted_results.append(result)
            
            return {
                "success": True,
                "query": query,
                "filters": filters,
                "count": len(formatted_results),
                "recommendations": formatted_results,
                "message": f"Found {len(formatted_results)} restaurant recommendations"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting recommendations: {str(e)}"
            }
    
    def get_similar_restaurants(self, restaurant_id: int, top_k: int = 3) -> Dict:
        """Get restaurants similar to a given restaurant"""
        try:
            restaurant = self.db.get_restaurant_by_id(restaurant_id)
            if not restaurant:
                return {"success": False, "error": "Restaurant not found"}
            
            query = f"{restaurant['cuisine']} restaurant with similar vibe to {restaurant['name']}"
            
            similar = self.embeddings.semantic_search(query, top_k=top_k + 1)
            # Remove the restaurant itself
            similar = [r for r in similar if r['id'] != restaurant_id][:top_k]
            
            return {
                "success": True,
                "original_restaurant": restaurant['name'],
                "similar_restaurants": similar
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error finding similar restaurants: {str(e)}"
            }
