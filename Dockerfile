# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variable for Flask (needed by Flask-Migrate etc.)
ENV FLASK_APP=backend/app.py

# Expose the port the app runs on
EXPOSE 5000

# Command to run database migrations (run this once per deployment)
# This is often done as part of the Render deploy hook or start command
# CMD ["flask", "db", "upgrade"] # Can run this before starting the server

# Command to run the application with Gunicorn and Eventlet workers for SocketIO
# Install eventlet: pip install eventlet
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "wsgi:socketio"]
# -w 1: Use 1 worker process. Scale instances in Render.
# -k eventlet: Use the eventlet worker class required by Flask-SocketIO
# wsgi:socketio: Tell gunicorn to run the socketio.run() call in wsgi.py
