from deriv_api import DerivAPI

deriv_api_token = "QoJw6lc5q0Z6n7X"        # Hardcoded for now, should be stored securely
deriv_app_id = 125387                      # Hardcoded for now, should be stored securely

# Lazy initialization - DerivAPI requires async event loop
# Don't create at import time, create when needed
_deriv_api = None

def get_deriv_api():
    """Get or create the DerivAPI instance (lazy initialization)."""
    global _deriv_api
    if _deriv_api is None:
        _deriv_api = DerivAPI(app_id=deriv_app_id)
    return _deriv_api

# For backwards compatibility - but prefer using get_deriv_api()
deriv_api = None  # Will be set on first async call