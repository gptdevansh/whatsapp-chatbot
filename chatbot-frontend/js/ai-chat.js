/**
 * AI Chat Page - Direct AI Testing Interface
 * 
 * Allows admins to chat directly with the AI without WhatsApp.
 * Useful for testing AI responses and conversation quality.
 */

// Verify authentication on page load
if (!localStorage.getItem('token')) {
  window.location.href = 'index.html';
}

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');

/**
 * Auto-resize textarea as user types
 */
messageInput.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + 'px';
});

/**
 * Handle keyboard shortcuts
 * Enter to send, Shift+Enter for new line
 */
function handleKeyPress(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

/**
 * Send message to AI and display response
 */
async function sendMessage() {
  const message = messageInput.value.trim();
  
  if (!message) return;
  
  // Display user message immediately
  addMessage('user', message);
  messageInput.value = '';
  messageInput.style.height = 'auto';
  
  // Show loading state
  sendButton.disabled = true;
  typingIndicator.classList.add('active');
  
  try {
    // Call AI chat endpoint
    const response = await fetch('/api/v1/admin/ai-chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('token')
      },
      body: JSON.stringify({ message })
    });
    
    // Handle authentication errors
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
    showToast("Failed to get AI response. Please try again.", "error");
    addMessage('ai', 'Sorry, I encountered an error. Please try again.');
    
  } finally {
    sendButton.disabled = false;
  }
}

/**
 * Add message to chat interface
 * 
 * @param {string} type - Message type: 'user' or 'ai'
 * @param {string} content - Message text content
 */
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
  scrollToBottom();
}

/**
 * Smooth scroll to bottom of chat
 */
function scrollToBottom() {
  requestAnimationFrame(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  });
}

/**
 * Clear all chat messages
 */
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
    showToast("Chat cleared successfully", "success");
  }
}

/**
 * Escape HTML to prevent XSS attacks
 * 
 * @param {string} text - Text to escape
 * @returns {string} HTML-safe text
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Show toast notification
 * 
 * @param {string} message - Message to display
 * @param {string} type - Toast type: success, error, warning, info
 */
function showToast(message, type = "info") {
  const bgColors = {
    error: "linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%)",
    success: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)",
    warning: "linear-gradient(135deg, #ffa94d 0%, #f76707 100%)",
    info: "linear-gradient(135deg, #339af0 0%, #1971c2 100%)"
  };

  Toastify({
    text: message,
    duration: 3000,
    gravity: "top",
    position: "right",
    style: {
      background: bgColors[type] || bgColors.info,
    }
  }).showToast();
}

// Focus input on page load
messageInput.focus();
