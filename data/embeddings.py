"""
Embedding Manager
Pre-compute and cache restaurant embeddings for semantic search
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from data.db_manager import DatabaseManager

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.db = DatabaseManager()
        self.restaurant_embeddings = {}
        self.restaurants_cache = []
    
    def generate_restaurant_text(self, restaurant: Dict) -> str:
        """Generate text representation of restaurant for embedding"""
        features = json.loads(restaurant['special_features'])
        features_str = ", ".join(features)
        
        text = f"{restaurant['name']} is a {restaurant['cuisine']} restaurant in {restaurant['location']}. "
        text += f"Rating: {restaurant['rating']}/5. Price range: {restaurant['price_range']}. "
        text += f"Features: {features_str}. {restaurant['description']}"
        
        return text
    
    def compute_embeddings(self):
        """Compute embeddings for all restaurants"""
        print("🔄 Computing restaurant embeddings...")
        
        restaurants = self.db.get_restaurants()
        self.restaurants_cache = restaurants
        
        texts = [self.generate_restaurant_text(r) for r in restaurants]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        for i, restaurant in enumerate(restaurants):
            self.restaurant_embeddings[restaurant['id']] = embeddings[i]
        
        print(f"✅ Computed embeddings for {len(restaurants)} restaurants")
    
    def semantic_search(self, query: str, top_k: int = 5, filters: Dict = None) -> List[Dict]:
        """Search restaurants using semantic similarity"""
        if not self.restaurant_embeddings:
            self.compute_embeddings()
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Apply filters first
        filtered_restaurants = self.restaurants_cache
        if filters:
            filtered_restaurants = [
                r for r in self.restaurants_cache
                if self._matches_filters(r, filters)
            ]
        
        if not filtered_restaurants:
            return []
        
        # Compute similarities
        similarities = []
        for restaurant in filtered_restaurants:
            rest_embedding = self.restaurant_embeddings[restaurant['id']]
            similarity = cosine_similarity([query_embedding], [rest_embedding])[0][0]
            similarities.append((restaurant, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k with scores
        results = []
        for restaurant, score in similarities[:top_k]:
            result = restaurant.copy()
            result['similarity_score'] = float(score)
            results.append(result)
        
        return results
    
    def _matches_filters(self, restaurant: Dict, filters: Dict) -> bool:
        """Check if restaurant matches filters"""
        if 'cuisine' in filters and restaurant['cuisine'] != filters['cuisine']:
            return False
        
        if 'location' in filters and filters['location'].lower() not in restaurant['location'].lower():
            return False
        
        if 'min_rating' in filters and restaurant['rating'] < filters['min_rating']:
            return False
        
        if 'price_range' in filters and restaurant['price_range'] != filters['price_range']:
            return False
        
        return True
    
    def hybrid_search(self, query: str, filters: Dict = None, top_k: int = 5) -> List[Dict]:
        """Hybrid search combining semantic similarity and structured filters"""
        # Get semantic results
        semantic_results = self.semantic_search(query, top_k=top_k * 2, filters=filters)
        
        # Re-rank based on rating and availability
        for result in semantic_results:
            # Boost score based on rating
            rating_boost = (result['rating'] / 5.0) * 0.2
            result['final_score'] = result['similarity_score'] + rating_boost
        
        # Sort by final score
        semantic_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return semantic_results[:top_k]
