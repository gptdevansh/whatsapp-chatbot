// Chats Page JS - Fetches and renders recent chats

document.addEventListener('DOMContentLoaded', async function() {
  // Auth check
  if (!localStorage.getItem('token')) {
    window.location.href = 'index.html';
    return;
  }
  
  const chatsList = document.getElementById('chatsList');
  
  try {
    const res = await fetch('/api/v1/admin/chats/latest', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    
    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
        return;
      }
      throw new Error('Failed to fetch');
    }
    
    const chats = await res.json();
    chatsList.innerHTML = '';
    
    if (chats.length === 0) {
      chatsList.innerHTML = '<div style="text-align:center;padding:3rem;color:var(--text-muted);">No messages yet</div>';
      return;
    }
    
    chats.forEach((chat, index) => {
      const div = document.createElement('div');
      div.className = 'chat-message';
      div.style.animationDelay = `${index * 0.05}s`;
      
      const roleColor = chat.role === 'user' ? 'var(--primary)' : 'var(--accent)';
      const roleLabel = chat.role === 'user' ? 'User' : 'AI';
      
      div.innerHTML = `
        <div class="chat-meta">
          <b style="color:${roleColor}">${roleLabel}:</b> ${chat.user_name || 'Unknown'} 
          | <b>Time:</b> ${new Date(chat.timestamp).toLocaleString()}
        </div>
        <div style="line-height:1.6;margin-top:0.5rem;">${chat.message}</div>
      `;
      chatsList.appendChild(div);
    });
  } catch (err) {
    chatsList.innerHTML = '<div style="color:var(--error);text-align:center;padding:3rem;">Error loading messages. Please try again.</div>';
  }
});

