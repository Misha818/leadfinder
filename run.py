import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Retrieve port and debug settings from environment, or use defaults
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']

    print(f"Starting Company Finder server at http://{host}:{port}...")
    app.run(host=host, port=port, debug=debug)
