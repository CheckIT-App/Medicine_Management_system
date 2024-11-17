import logging
import uvicorn

def start_server():
    uvicorn.run(
        "app.main:app",  # Use the full module path
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
