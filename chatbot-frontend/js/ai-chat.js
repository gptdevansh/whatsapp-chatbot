// AI Chat JS - Admin can chat with AI directly

// Auth check
if (!localStorage.getItem('token')) {
  window.location.href = 'index.html';
}

const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');

// Auto-resize textarea
messageInput.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + 'px';
});

// Handle Enter key (Shift+Enter for new line)
function handleKeyPress(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

// Send message to AI
async function sendMessage() {
  const message = messageInput.value.trim();
  
  if (!message) return;
  
  // Add user message to chat
  addMessage('user', message);
  messageInput.value = '';
  messageInput.style.height = 'auto';
  
  // Disable send button
  sendButton.disabled = true;
  typingIndicator.classList.add('active');
  
  try {
    const response = await fetch('/api/v1/admin/ai-chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('token')
      },
      body: JSON.stringify({ message })
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
        return;
      }
      throw new Error('Failed to get AI response');
    }
    
    const data = await response.json();
    
    // Simulate typing delay for better UX
    setTimeout(() => {
      typingIndicator.classList.remove('active');
      addMessage('ai', data.response || data.message || 'I apologize, but I could not generate a response.');
    }, 800);
    
  } catch (error) {
    typingIndicator.classList.remove('active');
    
    Toastify({
      text: "Failed to get AI response. Please try again.",
      duration: 3000,
      gravity: "top",
      position: "right",
      style: {
        background: "linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%)",
      }
    }).showToast();
    
    addMessage('ai', 'Sorry, I encountered an error. Please try again.');
  } finally {
    sendButton.disabled = false;
  }
}

// Add message to chat UI
function addMessage(type, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;
  
  const avatar = type === 'user' ? 'You' : 'AI';
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  messageDiv.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">
      <p>${escapeHtml(content)}</p>
      <span class="message-time">${time}</span>
    </div>
  `;
  
  chatMessages.appendChild(messageDiv);
  
  // Scroll to bottom - use multiple methods to ensure it works
  scrollToBottom();
}

// Scroll chat to bottom
function scrollToBottom() {
  requestAnimationFrame(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  });
}

// Clear chat
function clearChat() {
  if (confirm('Are you sure you want to clear all messages?')) {
    chatMessages.innerHTML = `
      <div class="message ai">
        <div class="message-avatar">AI</div>
        <div class="message-content">
          <p>Hello! I'm your AI assistant powered by Llama 3.3 70B. How can I help you today?</p>
          <span class="message-time">Just now</span>
        </div>
      </div>
    `;
    
    scrollToBottom();
    
    Toastify({
      text: "Chat cleared successfully",
      duration: 2000,
      gravity: "top",
      position: "right",
      style: {
        background: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)",
      }
    }).showToast();
  }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Focus input on load
messageInput.focus();
