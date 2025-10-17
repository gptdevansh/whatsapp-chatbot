/**
 * Chats Page - Recent Conversations Viewer
 * 
 * Displays the latest chat messages across all users.
 * Shows both user messages and AI responses with timestamps.
 */

document.addEventListener('DOMContentLoaded', async function() {
  // Verify authentication
  if (!localStorage.getItem('token')) {
    window.location.href = 'index.html';
    return;
  }
  
  const chatsList = document.getElementById('chatsList');
  
  try {
    // Fetch recent chats from backend
    const res = await fetch('/api/v1/admin/chats/latest', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    
    // Handle authentication errors
    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
        return;
      }
      throw new Error('Failed to fetch chats');
    }
    
    const chats = await res.json();
    
    renderChats(chats, chatsList);
    
  } catch (err) {
    chatsList.innerHTML = '<div style="color:var(--error);text-align:center;padding:3rem;">Error loading messages. Please try again.</div>';
  }
});

/**
 * Render chat messages
 * 
 * @param {Array} chats - Array of chat message objects
 * @param {HTMLElement} container - Container element for messages
 */
function renderChats(chats, container) {
  container.innerHTML = '';
  
  // Handle empty state
  if (chats.length === 0) {
    container.innerHTML = '<div style="text-align:center;padding:3rem;color:var(--text-muted);">No messages yet</div>';
    return;
  }
  
  // Render each chat message with staggered animation
  chats.forEach((chat, index) => {
    const div = document.createElement('div');
    div.className = 'chat-message';
    div.style.animationDelay = `${index * 0.05}s`;
    
    // Style based on message role
    const roleColor = chat.role === 'user' ? 'var(--primary)' : 'var(--accent)';
    const roleLabel = chat.role === 'user' ? 'User' : 'AI';
    
    div.innerHTML = `
      <div class="chat-meta">
        <b style="color:${roleColor}">${roleLabel}:</b> ${chat.user_name || 'Unknown'} 
        | <b>Time:</b> ${formatTimestamp(chat.timestamp)}
      </div>
      <div style="line-height:1.6;margin-top:0.5rem;">${escapeHtml(chat.message)}</div>
    `;
    
    container.appendChild(div);
  });
}

/**
 * Format ISO timestamp to readable format
 * 
 * @param {string} timestamp - ISO timestamp string
 * @returns {string} Formatted date and time
 */
function formatTimestamp(timestamp) {
  return new Date(timestamp).toLocaleString();
}

/**
 * Escape HTML to prevent XSS
 * 
 * @param {string} text - Text to escape
 * @returns {string} HTML-safe text
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

