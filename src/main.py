from autoscraper24_api.app import app
import uvicorn

def run_app(host="0.0.0.0", port=8000, reload=False):
    """
    Run the FastAPI application with uvicorn.
    
    Args:
        host (str): Host to bind the server to
        port (int): Port to bind the server to
        reload (bool): Whether to reload the server on code changes
    """
    uvicorn.run("autoscraper24_api.app:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    run_app(reload=True)