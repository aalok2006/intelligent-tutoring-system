from flask_socketio import SocketIO, emit, join_room, leave_room
from .app import socketio # Import socketio instance from app.py
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..services.chat_service import ChatService
from ..services.ai_tutor_service import AI TutorService # For AI Tutor responses

chat_service = ChatService()
ai_tutor_service = AI TutorService()

# Custom decorator to authenticate SocketIO connections using JWT
def authenticated_only(f):
    # Using functools.wraps to preserve original function metadata
    import functools
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            verify_jwt_in_request() # Verifies token in connection handshake headers or query args
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Socket authentication failed: {e}") # Log failure
            # Disconnect or send error? Let's log for now.
            # Note: Handling authentication in SocketIO handshakes correctly
            # requires specific setup on client and server. JWT in headers is common.
            # For simplicity in this example, we assume verify_jwt_in_request works.
            # A more robust approach might use a separate token passed in connect args.
            pass # Allow function to proceed, but user_id will be None if auth failed
    return wrapped


@socketio.on('connect')
@authenticated_only # Protect connection
def handle_connect():
    user_id = get_jwt_identity()
    print(f'Client connected: {request.sid} (User ID: {user_id})')
    if user_id:
        # Associate socket ID with user ID if authentication successful
        # Need a mechanism to map socket ID to user ID, e.g., a Redis store or global dict (careful with multiple servers)
        # chat_service.associate_user_with_socket(user_id, request.sid) # Service method needed
        emit('status', {'msg': 'Connected!', 'user_id': user_id})
        # User joins relevant chat rooms (e.g., general subject chat, their private AI chat)
        # Example: Join the AI Tutor room for this user
        ai_tutor_channel_id = chat_service.get_or_create_ai_tutor_channel(user_id) # Service method needed
        join_room(f'channel_{ai_tutor_channel_id}')
        print(f"User {user_id} joined room channel_{ai_tutor_channel_id}")

        # Also join other channels the user is a member of (e.g., Subject Q&A)
        # user_channels = chat_service.get_user_channels(user_id)
        # for channel in user_channels:
        #      join_room(f'channel_{channel.id}')
        #      print(f"User {user_id} joined room channel_{channel.id}")


@socketio.on('disconnect')
def handle_disconnect():
    user_id = get_jwt_identity() # Might not work if token expired/not sent on disconnect
    print(f'Client disconnected: {request.sid} (User ID: {user_id if user_id else "unknown"})')
    # Clean up socket-user association if needed
    # chat_service.dissociate_socket(request.sid)


@socketio.on('join_channel')
@authenticated_only
def handle_join_channel(data):
    user_id = get_jwt_identity()
    channel_id = data.get('channel_id')
    if user_id and channel_id:
        # Check if user is allowed to join this channel (e.g., is member)
        if chat_service.is_user_in_channel(user_id, channel_id): # Service method needed
            join_room(f'channel_{channel_id}')
            print(f'User {user_id} joined channel {channel_id} room.')
            emit('status', {'msg': f'Joined channel {channel_id}'}, room=request.sid) # Only to the sender
            # Optional: Notify others in channel that user joined
            # emit('user_joined', {'user_id': user_id}, room=f'channel_{channel_id}')
        else:
            emit('error', {'msg': 'Not authorized to join channel'}, room=request.sid)
    else:
         emit('error', {'msg': 'Invalid request'}, room=request.sid)


@socketio.on('leave_channel')
@authenticated_only
def handle_leave_channel(data):
    user_id = get_jwt_identity()
    channel_id = data.get('channel_id')
    if user_id and channel_id:
        leave_room(f'channel_{channel_id}')
        print(f'User {user_id} left channel {channel_id} room.')
        emit('status', {'msg': f'Left channel {channel_id}'}, room=request.sid)


@socketio.on('message')
@authenticated_only
def handle_message(data):
    user_id = get_jwt_identity()
    channel_id = data.get('channel_id')
    message_text = data.get('text')

    if user_id and channel_id and message_text:
        # Check if user is in the channel or allowed to send messages
        if chat_service.is_user_in_channel(user_id, channel_id) or channel_id == chat_service.get_or_create_ai_tutor_channel(user_id): # Allow sending to AI tutor channel even if not "joined" room yet
            print(f"Received message from user {user_id} in channel {channel_id}: {message_text}")

            # Save message to DB (Phase 1)
            saved_message = chat_service.save_message(user_id, channel_id, message_text) # Service method needed
            if not saved_message:
                 print("Failed to save message.")
                 return # Don't process further if save failed

            # Broadcast message to others in the channel's room
            message_data = {
                'id': saved_message.id,
                'channel_id': saved_message.channel_id,
                'sender_id': saved_message.sender_id,
                'timestamp': saved_message.timestamp.isoformat(), # Send as ISO string
                'text': saved_message.message_text,
                'sender_username': chat_service.get_user_username(saved_message.sender_id) # Need to fetch username
                # Add other data like file_attachments, mentions, reply_to_message_id in later phases
            }
            emit('new_message', message_data, room=f'channel_{channel_id}', include_self=True) # Send back to sender too

            # If it's the AI Tutor channel, process the message with the AI Tutor
            if chat_service.is_ai_tutor_channel(channel_id): # Service method needed
                 # This should be asynchronous to avoid blocking the SocketIO event loop
                 # Use Celery task for AI processing
                 from ..tasks import process_ai_tutor_message_task # Import the task
                 process_ai_tutor_message_task.delay(user_id, channel_id, message_text)
                 # The task will save the AI's response and emit 'new_message'

        else:
            emit('error', {'msg': 'Not authorized to send messages in this channel'}, room=request.sid)
    else:
        emit('error', {'msg': 'Invalid message data'}, room=request.sid)


# Need basic service methods in services/chat_service.py
# Need AI processing task in tasks.py
