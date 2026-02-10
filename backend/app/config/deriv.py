from deriv_api import DerivAPI
import asyncio

deriv_api_token = "QoJw6lc5q0Z6n7X"        # Hardcoded for now, should be stored securely
deriv_app_id = 125387                      # Hardcoded for now, should be stored securely
_deriv_api_instance = None

def get_deriv_api():
    """Get the configured Deriv API instance, lazy-loaded."""
    global _deriv_api_instance
    if _deriv_api_instance is None:
        _deriv_api_instance = DerivAPI(app_id=deriv_app_id)
    return _deriv_api_instance
