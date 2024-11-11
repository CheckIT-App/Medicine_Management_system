from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import gettext
import os

# Define the path to the translations folder
locale_path = os.path.join(os.path.dirname(__file__), "translations")

# Define the language middleware
class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract the language from the path; default to "he" if none is found
        path_parts = request.url.path.strip("/").split("/")
        lang = path_parts[0] if path_parts[0] in ["en", "he"] else "he"
        # Load the translation function for the specified language
        try:
            translation = gettext.translation("messages", localedir=locale_path, languages=[lang], fallback=True)
            translation.install()
            request.state._ = translation.gettext  # Store translation function in request state
        except FileNotFoundError:
            # Fallback to default if translation file not found
            gettext.install("messages", localedir=locale_path, fallback=True)
            request.state._ = gettext.gettext

        # Proceed with the request
        response = await call_next(request)
        return response
