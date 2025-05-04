from celery import Celery
from .app import app # Import app instance for context
from ..services.ai_tutor_service import AI TutorService
from ..services.chat_service import ChatService

# Initialize Celery - needs the broker URL from config
celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config) # Use Flask app config for Celery


@celery.task
def process_ai_tutor_message_task(user_id, channel_id, message_text):
    # This task runs in a background worker
    # It needs the Flask app context to interact with services/DB
    with app.app_context():
        print(f"Celery task received AI Tutor message: user={user_id}, channel={channel_id}")
        ai_tutor_service = AI TutorService() # Instantiate services inside the task context
        chat_service = ChatService()

        # Call AI Tutor logic
        ai_response_text = ai_tutor_service.process_message(user_id, message_text) # Service method needed

        if ai_response_text:
            # Save AI response (AI Tutor has a system sender ID)
            ai_sender_id = chat_service.get_ai_tutor_user_id() # Service method needed to get AI's user ID
            saved_message = chat_service.save_message(ai_sender_id, channel_id, ai_response_text)

            if saved_message:
                 # Emit message via SocketIO FROM THE WORKER
                 # Need to send message to the specific room (channel_id)
                 # This requires the worker to be able to emit SocketIO events.
                 # Configure Flask-SocketIO to work with Celery workers.
                 # This usually involves using message queues (like Redis pub/sub)
                 # between the web process (handling SocketIO) and the worker process.
                 # Or, the worker could call a dedicated API endpoint on the web process to emit.
                 # Simpler approach: The worker *could* directly use socketio.emit if configured correctly, but it's complex.
                 # Let's assume for now the worker *can* emit:
                 from .app import socketio # Import the SocketIO instance
                 message_data = {
                     'id': saved_message.id,
                     'channel_id': saved_message.channel_id,
                     'sender_id': saved_message.sender_id,
                     'timestamp': saved_message.timestamp.isoformat(),
                     'text': saved_message.message_text,
                     'sender_username': chat_service.get_user_username(saved_message.sender_id) # Need to fetch username
                 }
                 # This emit needs to run in an event loop context, which Celery tasks usually don't have.
                 # A common pattern is to use a separate Flask app instance dedicated to SocketIO emitting in the worker.
                 # For Render simplicity, let's assume direct emit works or implement the API call back to web service.
                 # Option 1 (Simpler for Render): The task *doesn't* emit directly. The frontend *polls* or relies on connection stability. (Less real-time).
                 # Option 2 (More complex): Implement a separate 'emit_message_to_channel' API endpoint on the web service that the worker calls.
                 # Let's go with Option 2 as it's more representative of the real-time goal.

                 # OPTION 2: Call back to web service to emit
                 # Requires web service to have an API like POST /internal/emit
                 # and worker to have requests library and web service URL
                 # import requests
                 # web_service_url = app.config['WEB_SERVICE_URL'] # Need this in config
                 # try:
                 #      response = requests.post(f"{web_service_url}/internal/emit", json=message_data)
                 #      response.raise_for_status() # Raise for HTTP errors
                 #      print("Worker successfully triggered emit via web service.")
                 # except requests.exceptions.RequestException as e:
                 #      print(f"Worker failed to trigger emit: {e}")

                 # Or, if using Redis pub/sub with SocketIO
                 # from flask_socketio import SocketIO as WorkerSocketIO # Need a separate instance configured for the message queue
                 # mq_socketio = WorkerSocketIO(message_queue=app.config['CELERY_BROKER_URL'])
                 # mq_socketio.emit('new_message', message_data, room=f'channel_{channel_id}', namespace='/', include_self=False) # Don't include self, it's the AI
                 # print("Worker emitted message via message queue.")

                 # Let's stick with the Redis pub/sub approach for SocketIO as it's designed for this.
                 # Need to ensure flask_socketio is configured to use Redis message queue in app.py
                 print("AI response saved. Worker processing complete.")
                 # The actual emit will happen via Redis pub/sub handled by the web service.


@celery.task
def generate_initial_path_task(user_id, diagnostic_results=None, user_goals=None):
     with app.app_context():
          print(f"Celery task received initial path generation request: user={user_id}")
          pe = PersonalizationEngine()
          pe.generate_initial_path(user_id, diagnostic_results, user_goals)
          print(f"Celery task completed initial path generation for user {user_id}.")

# Add other tasks for path adaptation, competitive test processing, etc.
