from deriv_api import DerivAPI
import asyncio

deriv_api_token = "QoJw6lc5q0Z6n7X"        # Hardcoded for now, should be stored securely
deriv_app_id = 125387                      # Hardcoded for now, should be stored securely
# _deriv_api_instance = None

# def get_deriv_api():
#     """Get the configured Deriv API instance, lazy-loaded and reconnect if closed."""
#     global _deriv_api_instance

#     reconnect = False

#     if _deriv_api_instance is None:
#         reconnect = True
#     else:
#         # Check if the WebSocket inside DerivAPI exists and is open
#         try:
#             # Some DerivAPI clients use self.ws.sock.connected
#             if not getattr(_deriv_api_instance, 'ws', None) or not getattr(_deriv_api_instance.ws, 'sock', None) or not _deriv_api_instance.ws.sock.connected:
#                 reconnect = True
#         except Exception:
#             reconnect = True

#     if reconnect:
#         _deriv_api_instance = DerivAPI(app_id=deriv_app_id)

#     return _deriv_api_instance
