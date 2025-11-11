"""
Google OAuth Helper
Handles Google Sign-In authentication
"""

import os
import json
from typing import Dict, Optional
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow

class GoogleOAuth:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_CALLBACK_URL", "http://localhost:8501")
        
        # Scopes for Google OAuth
        self.scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    
    def get_authorization_url(self) -> str:
        """Generate Google OAuth authorization URL"""
        try:
            # Create flow instance
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Generate authorization URL
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return authorization_url
            
        except Exception as e:
            print(f"Error generating authorization URL: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify Google ID token and extract user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.client_id
            )
            
            # Extract user information
            user_info = {
                "google_id": idinfo.get("sub"),
                "email": idinfo.get("email"),
                "full_name": idinfo.get("name"),
                "given_name": idinfo.get("given_name"),
                "family_name": idinfo.get("family_name"),
                "profile_picture": idinfo.get("picture"),
                "email_verified": idinfo.get("email_verified", False)
            }
            
            return user_info
            
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
    
    def get_user_info_from_code(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for user info"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for token
            flow.fetch_token(code=code)
            
            # Get credentials
            credentials = flow.credentials
            
            # Verify ID token
            idinfo = id_token.verify_oauth2_token(
                credentials.id_token,
                requests.Request(),
                self.client_id
            )
            
            user_info = {
                "google_id": idinfo.get("sub"),
                "email": idinfo.get("email"),
                "full_name": idinfo.get("name"),
                "profile_picture": idinfo.get("picture"),
                "email_verified": idinfo.get("email_verified", False)
            }
            
            return user_info
            
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
