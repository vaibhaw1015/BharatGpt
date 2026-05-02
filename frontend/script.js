const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const imageUpload = document.getElementById('image-upload');
const imagePreviewContainer = document.getElementById('image-preview-container');
const imagePreview = document.getElementById('image-preview');
const removeImageBtn = document.getElementById('remove-image-btn');

let currentImageBase64 = null;

// Dynamic API URL that works both locally and on Render
const API_URL = `${window.location.origin}/api/chat`;


function addMessage(message, isUser = false, imageBase64 = null, modelName = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.innerHTML = isUser ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content');
    
    // Convert message to markdown if AI, or simple text if user
    let finalHtml = '';
    
    // Add image if present
    if (imageBase64) {
        finalHtml += `<img src="${imageBase64}" class="chat-image" alt="Uploaded Image"><br>`;
    }

    if (isUser) {
        finalHtml += `<p>${message.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, '<br>')}</p>`;
    } else {
        if (modelName) {
            finalHtml += `<div class="model-badge">${modelName}</div>`;
        }
        finalHtml += marked.parse(message);
    }
    
    contentDiv.innerHTML = finalHtml;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    chatBox.appendChild(messageDiv);
    scrollToBottom();
}

function addTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'ai-message');
    messageDiv.setAttribute('id', 'typing-indicator');

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content');
    contentDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    chatBox.appendChild(messageDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function handleSend() {
    const query = userInput.value.trim();
    if (!query && !currentImageBase64) return;

    const userMessage = query || "Attached an image.";
    const sentImageBase64 = currentImageBase64;

    // Display user message with image
    addMessage(userMessage, true, sentImageBase64);
    
    userInput.value = '';
    clearImagePreview();

    // Show typing indicator
    addTypingIndicator();

    try {
        // Extract just the base64 part, removing the data URL prefix if it exists
        let rawBase64 = null;
        if (sentImageBase64) {
            rawBase64 = sentImageBase64.split(',')[1] || sentImageBase64;
        }

        const payload = { 
            query: userMessage,
            ...(rawBase64 && { image_base64: rawBase64 })
        };

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        removeTypingIndicator();

        if (response.ok) {
            addMessage(data.answer, false, null, data.model_used);
        } else {
            addMessage('Sorry, there was an error processing your request. Please check if the backend is running.', false);
            console.error('Server Error:', data);
        }

    } catch (error) {
        removeTypingIndicator();
        addMessage(`Network error: Could not connect to the Bharat GPT server. Please try again in a few seconds while the server wakes up. (Details: ${error.message})`, false);
        console.error('Fetch Error:', error);
    }
}

sendBtn.addEventListener('click', handleSend);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSend();
    }
});

// Image Upload Logic
imageUpload.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            currentImageBase64 = event.target.result;
            imagePreview.src = currentImageBase64;
            imagePreviewContainer.style.display = 'flex';
        };
        reader.readAsDataURL(file);
    }
});

function clearImagePreview() {
    currentImageBase64 = null;
    imagePreview.src = '';
    imagePreviewContainer.style.display = 'none';
    imageUpload.value = '';
}

removeImageBtn.addEventListener('click', clearImagePreview);
