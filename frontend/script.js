const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// Backend API URL (assumes FastAPI is running on localhost:8000)
const API_URL = 'http://localhost:8000/chat';

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    const textDiv = document.createElement('div');
    textDiv.classList.add('text');
    textDiv.textContent = text;
    
    messageDiv.appendChild(textDiv);
    chatBox.appendChild(messageDiv);
    
    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message to UI
    addMessage(text, 'user');
    userInput.value = '';
    
    // Disable input while waiting
    userInput.disabled = true;
    sendButton.disabled = true;

    // Change button text to a loading spinner
    const originalButtonText = sendButton.innerHTML;
    sendButton.innerHTML = '<div class="spinner"></div>';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: text })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.answer, 'assistant');
    } catch (error) {
        console.error('Error fetching response:', error);
        addMessage(`Sorry, I encountered an error connecting to the server: ${error.message}`, 'assistant');
    } finally {
        // Re-enable input and return to original text
        userInput.disabled = false;
        sendButton.disabled = false;
        sendButton.innerHTML = originalButtonText;
        userInput.focus();
    }
}

// Listen for a click on the Send button
sendButton.addEventListener('click', () => {
    sendMessage();
});

// Listen for the "Enter" key in the input field
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});