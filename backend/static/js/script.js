document.addEventListener('DOMContentLoaded', () => {
    const authForms = document.getElementById('auth-forms');
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');
    const showRegisterBtn = document.getElementById('show-register');
    const showLoginBtn = document.getElementById('show-login');
    const registerBtn = document.getElementById('register-btn');
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout');
    const registerMessage = document.getElementById('register-message');
    const loginMessage = document.getElementById('login-message');
    const welcomeMessage = document.getElementById('welcome-message');
    const usernameDisplay = document.getElementById('username-display');
    const learningSection = document.getElementById('learning-section');
    const pathVisualization = document.getElementById('path-visualization');
    const chatChannelsDiv = document.getElementById('chat-channels');
    const chatWindowsDiv = document.getElementById('chat-windows');


    const API_URL = '/api'; // Relative URL

    // --- Authentication Handling ---

    function showAuthSection() {
        authForms.style.display = 'block';
        learningSection.style.display = 'none';
        welcomeMessage.style.display = 'none';
        logoutBtn.style.display = 'none';
        showRegisterBtn.style.display = 'inline-block';
        showLoginBtn.style.display = 'inline-block';
        setAuthToken(null); // Clear token on logout/show auth
    }

     function showLearningSection() {
        authForms.style.display = 'none';
        learningSection.style.display = 'block';
        welcomeMessage.style.display = 'inline-block';
        logoutBtn.style.display = 'inline-block';
        showRegisterBtn.style.display = 'none';
        showLoginBtn.style.display = 'none';
        // Load learning data
        loadLearningPath();
        setupChat(); // Setup chat after login
    }

    function setAuthToken(token) {
        if (token) {
            localStorage.setItem('authToken', token);
        } else {
            localStorage.removeItem('authToken');
        }
    }

    function getAuthToken() {
        return localStorage.getItem('authToken');
    }

    function checkAuth() {
        const token = getAuthToken();
        if (token) {
             // Optional: Verify token with backend or check expiration
             // For simplicity, assume if token exists, user is logged in
             // In a real app, you'd fetch user info and display username
             // For now, just show the learning section
             fetch(`${API_URL}/auth/protected`, { // Example of using token
                 headers: {
                     'Authorization': `Bearer ${token}`
                 }
             })
             .then(response => {
                 if (response.ok) {
                      return response.json();
                 } else {
                      throw new Error('Token invalid or expired');
                 }
             })
             .then(data => {
                 // Get actual username from user data endpoint if available
                 // For now, display a placeholder or try to get from local storage if saved on login
                 usernameDisplay.textContent = localStorage.getItem('username') || 'User'; // Assuming username saved on login
                 showLearningSection();
             })
             .catch(error => {
                 console.error("Auth check failed:", error);
                 showAuthSection(); // Go back to login if token is invalid
             });
        } else {
            showAuthSection();
        }
    }

    showRegisterBtn.addEventListener('click', () => {
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
        registerMessage.textContent = '';
        loginMessage.textContent = '';
    });

    showLoginBtn.addEventListener('click', () => {
        registerForm.style.display = 'none';
        loginForm.style.display = 'block';
        registerMessage.textContent = '';
        loginMessage.textContent = '';
    });

    registerBtn.addEventListener('click', () => {
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;

        fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        })
        .then(response => response.json())
        .then(data => {
            registerMessage.textContent = data.message;
            registerMessage.style.color = data.message.includes('success') ? 'green' : 'red';
            if (data.message.includes('success')) {
                // Optional: Auto-login after successful registration
                // Or show login form and prompt user to login
                showLoginBtn.click(); // Show login form
            }
        })
        .catch(error => {
            console.error('Registration error:', error);
            registerMessage.textContent = 'An error occurred during registration.';
            registerMessage.style.color = 'red';
        });
    });

    loginBtn.addEventListener('click', () => {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Login failed');
            }
        })
        .then(data => {
            setAuthToken(data.access_token);
            localStorage.setItem('username', username); // Save username locally for display
            usernameDisplay.textContent = username;
            showLearningSection();
            loginMessage.textContent = ''; // Clear message
        })
        .catch(error => {
            console.error('Login error:', error);
            loginMessage.textContent = 'Invalid username or password.';
            loginMessage.style.color = 'red';
        });
    });

    logoutBtn.addEventListener('click', () => {
        // Invalidate token on backend if necessary (optional)
        showAuthSection(); // Clear token and show login forms
        usernameDisplay.textContent = '';
        localStorage.removeItem('username');
        // Disconnect socket if connected
        if (socket) {
            socket.disconnect();
        }
    });


    // --- Learning Path Handling (FR1.5) ---

    function loadLearningPath() {
        const token = getAuthToken();
        if (!token) return;

        fetch(`${API_URL}/path/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else if (response.status === 404) {
                 pathVisualization.innerHTML = '<p>No learning path generated yet. Please complete the diagnostic assessment.</p>';
                 return null; // Or handle initial diagnostic trigger if applicable
            }
            throw new Error('Failed to load learning path');
        })
        .then(pathData => {
            if (pathData) {
                 renderLearningPath(pathData); // Call function to display path
            }
        })
        .catch(error => {
            console.error('Error loading path:', error);
            pathVisualization.innerHTML = '<p>Error loading learning path.</p>';
        });
    }

    function renderLearningPath(pathData) {
        // Simple text rendering for Phase 1 (FR1.5 needs visual)
        let html = '<h3>Path ID: ' + pathData.path_id + '</h3>';
        html += '<p>Current Node: ' + (pathData.current_node_id || 'None') + '</p>';
        html += '<h4>Nodes:</h4><ul>';
        pathData.nodes.sort((a, b) => a.order - b.order).forEach(node => {
            html += `<li>Node ${node.order}: ${node.title} (${node.type}) - Status: ${node.status}</li>`;
        });
        html += '</ul>';

        // TODO: Implement actual visual representation (SVG, Canvas, library)
        // using pathData.nodes and pathData.connections
        // Example structure for a visual node:
        // <div class="path-node" data-node-id="${node.id}" data-status="${node.status}">
        //     ${node.title}
        // </div>
        // You would then draw lines between these nodes based on connections data.

        pathVisualization.innerHTML = html;

         // For Phase 1 testing (Manual QA-FR1.5-001), check if this basic info is displayed.
         // Actual visual check requires rendering UI elements.
    }


    // --- Multi-Chat Handling (FR5.1, FR5.2, FR5.4, FR5.3 basic) ---

    let socket; // Variable to hold the SocketIO connection

    function setupChat() {
        const token = getAuthToken();
        if (!token) return;

        // Connect to the SocketIO server, sending token for authentication
        // Pass token in query parameters or handshake headers (headers preferred for security)
        // Flask-SocketIO verify_jwt_in_request checks headers by default.
        // If running on Render, use the public web service URL.
        // window.location.origin provides the scheme and host (e.g., http://localhost:5000 or https://your-app.onrender.com)
        socket = io(window.location.origin, {
            auth: {
               token: token // Pass the JWT token in the 'auth' object
            }
            // If headers don't work easily, you might pass it in query:
            // query: { token: token } // Less secure, visible in URL/logs
        });

        // --- Socket Event Listeners ---
        socket.on('connect', () => {
            console.log('Socket.IO connected!');
            // Once connected, the backend should handle joining the user to their channels (e.g., AI Tutor)
            // Frontend should request channel list and show available channels.
            // For Phase 1, we have a hardcoded AI Tutor channel button.
            // In Phase 2+, fetch available channels dynamically:
            // fetch(`${API_URL}/chat/channels`, { headers: { 'Authorization': ... } })
            // .then(response => response.json()).then(channels => renderChannels(channels));
        });

        socket.on('disconnect', () => {
            console.log('Socket.IO disconnected!');
            // Handle UI changes on disconnect if necessary
        });

        socket.on('new_message', (msg) => {
            console.log('New message:', msg);
            displayMessage(msg); // Function to add message to the correct chat window
            handleNewMessageNotification(msg.channel_id); // Handle notifications (Phase 1 basic)
        });

        socket.on('status', (data) => {
             console.log('Status:', data.msg);
             // Handle connection status messages
        });

        socket.on('error', (data) => {
             console.error('Socket error:', data.msg);
             // Display error to user
        });

        // --- Frontend Chat UI Logic ---

        // Add event listeners for sending messages
        chatWindowsDiv.querySelectorAll('.send-message-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                const chatWindow = event.target.closest('.chat-window');
                const channelId = chatWindow.dataset.channelId; // Get channel ID from data attribute
                const inputElement = chatWindow.querySelector('.message-input');
                const messageText = inputElement.value.trim();

                if (messageText && socket && socket.connected) {
                    socket.emit('message', { channel_id: channelId, text: messageText });
                    inputElement.value = ''; // Clear input field
                }
            });
        });

        // Allow sending message on Enter key
        chatWindowsDiv.querySelectorAll('.message-input').forEach(input => {
             input.addEventListener('keypress', (event) => {
                  if (event.key === 'Enter') {
                      event.preventDefault(); // Prevent default form submission if input is in a form
                      event.target.nextElementSibling.click(); // Trigger click on the send button
                  }
             });
        });


        // Add event listeners for switching channels (Phase 1 basic - AI Tutor only)
         chatChannelsDiv.querySelectorAll('.chat-channel-btn').forEach(button => {
              button.addEventListener('click', () => {
                   const targetChannelId = button.dataset.channelId;
                   // Hide all chat windows
                   chatWindowsDiv.querySelectorAll('.chat-window').forEach(win => win.style.display = 'none');
                   // Show the target window
                   document.getElementById(`chat-window-${targetChannelId}`).style.display = 'flex';
                   // Update active button state
                   chatChannelsDiv.querySelectorAll('.chat-channel-btn').forEach(btn => btn.classList.remove('active'));
                   button.classList.add('active');
                   // Optional: Request chat history for the selected channel if not already loaded
              });
         });

         // Initially activate the AI Tutor channel button and window
         chatChannelsDiv.querySelector('.chat-channel-btn[data-channel-type="ai_tutor"]').classList.add('active');
         chatWindowsDiv.querySelector('.chat-window[data-channel-id="ai-tutor-placeholder"]').style.display = 'flex';

         // Placeholder function to display a message
         function displayMessage(msg) {
              const chatWindow = chatWindowsDiv.querySelector(`.chat-window[data-channel-id="${msg.channel_id}"]`);
              if (chatWindow) {
                   const historyDiv = chatWindow.querySelector('.chat-history');
                   const messageElement = document.createElement('div');
                   messageElement.classList.add('chat-message');
                   // Basic message rendering (FR5.4)
                   // Needs refinement for sender identification, timestamps, formatting (FR5.5 later)
                   messageElement.innerHTML = `<strong>User ${msg.sender_id}</strong>: ${msg.text} <span class="timestamp">${new Date(msg.timestamp).toLocaleTimeString()}</span>`;
                   historyDiv.appendChild(messageElement);
                   // Auto-scroll to bottom
                   historyDiv.scrollTop = historyDiv.scrollHeight;
              }
         }

         // Placeholder function for basic notifications (FR5.3)
         function handleNewMessageNotification(channelId) {
              // For Phase 1, just a console log or simple alert.
              // In Phase 2+, update UI badges, play sound etc.
              const activeChannelWindow = chatWindowsDiv.querySelector('.chat-window:not([style*="display: none"])');
              const activeChannelId = activeChannelWindow ? activeChannelWindow.dataset.channelId : null;

              if (activeChannelId !== channelId) {
                   console.log(`New message in channel ${channelId}!`);
                   // Find the channel button and add a notification class/badge
                   const channelButton = chatChannelsDiv.querySelector(`.chat-channel-btn[data-channel-id="${channelId}"]`);
                   if (channelButton) {
                        // Add a simple visual indicator
                        channelButton.classList.add('has-new-messages'); // Define this CSS class
                        // Could also increment a counter badge
                   }
              }
         }
         // CSS for .has-new-messages would be needed in style.css
         // .chat-channel-btn.has-new-messages { border-color: red; } /* Example */


    } // End of setupChat function


    // --- Initial Load ---
    checkAuth(); // Check if user is already logged in via token

});

// Manual Test Guidance:
// QA-FR1.5-001: After logging in and path loads, inspect the #path-visualization div. Does it contain HTML representing nodes and connections (even if text-based initially)? Is the current node indicated?
// QA-FR5.1-001: After logging in, is the #chat-panel div visible?
// QA-FR5.2-001: Inside #chat-panel, is there a button/element for "AI Tutor"? (Hardcoded for Phase 1)
// QA-FR5.4-001: Log in two users (two different browsers/incognito windows). Use the AI Tutor chat (since it's the only channel). Type a message in one, hit send. Does it appear in both windows with text, sender info (ID initially), and a timestamp?
// QA-NFR6-001: Register a user, log out. Log back in. Is the learning path still there (if generated)?

// Automated Test Guidance (using pytest + requests/selenium):
// QA-FR1.1-001, 002, 003: Write a pytest test. Simulate user creation (POST to /api/auth/register). Then, simulate diagnostic results being processed (this requires an internal endpoint or mocking). Then, make a GET request to /api/path using the user's token. Assert the structure of the returned path data (nodes, order, type) matches the expected outcome based on the simulated diagnostic score/goals.
// QA-FR2.2-001, 003: Write a pytest test. Register/login a user to get a token. Use a tool/library that can simulate SocketIO client connection (e.g., `socketio-client` or `websocket-client`). Connect to the backend's SocketIO endpoint, passing the token. Send a message event like `{'channel_id': 'ai-tutor-placeholder', 'text': 'What is X?'}` (Need to figure out actual AI Tutor channel ID dynamically or have a known ID). Listen for `new_message` events. Assert that the AI response appears and matches expectations (gives definition for Q-001, refuses for Q-003).
// QA-WF4.1-001: Write a pytest test. Simulate the sequence: POST /api/auth/register -> (Ideally) POST /api/assessment/diagnostic-complete with results -> GET /api/path. Assert that the /api/path call succeeds and returns a path after the simulated workflow steps.
