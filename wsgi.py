# This file is used by Gunicorn to run the Flask app and SocketIO server
from backend.app import app, socketio

if __name__ == "__main__":
    # For production, use Gunicorn with the SocketIO worker
    # gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 wsgi:app
    # Or gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 wsgi:socketio # If using older gunicorn
    # Or, with modern gunicorn and uvicorn/eventlet workers:
    # gunicorn -k eventlet -w 1 wsgi:app # Need eventlet installed
    # Or use uvicorn workers if using ASGI framework like FastAPI/Starlette. Flask is WSGI.
    # The Flask-SocketIO docs recommend using `socketio.run()` with a production server like Eventlet or Gevent.
    # We'll use gunicorn with eventlet workers in the Dockerfile/render.yaml command.
    socketio.run(app, host='0.0.0.0', port=5000) # Port will be handled by Render
