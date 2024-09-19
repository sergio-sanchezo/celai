def build_headers(token: str):
    
    return {
            "Content-Type": "application/json",
            "api_access_token": f"{token}"
        }