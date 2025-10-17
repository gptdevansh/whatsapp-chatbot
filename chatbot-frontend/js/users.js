/**
 * Users Page - User Management Interface
 * 
 * Displays all registered WhatsApp users with their conversation counts.
 * Includes real-time search functionality for filtering users.
 */

let allUsers = []; // Global user cache for search

document.addEventListener('DOMContentLoaded', async function() {
  // Verify authentication
  if (!localStorage.getItem('token')) {
    window.location.href = 'index.html';
    return;
  }
  
  const tbody = document.getElementById('usersTableBody');
  
  try {
    // Fetch users from backend
    const res = await fetch('/api/v1/admin/users', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    
    // Handle authentication errors
    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
        return;
      }
      throw new Error('Failed to fetch users');
    }
    
    const data = await res.json();
    allUsers = data.users || data;
    
    renderUsers(allUsers);
    showToast(`Loaded ${allUsers.length} users`, "success");
    
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:3rem;color:var(--error);">Error loading users. Please try again.</td></tr>';
    showToast("Failed to load users", "error");
  }
});

/**
 * Real-time search functionality
 * Filters users by name, phone number, or ID
 */
document.getElementById('searchUsers').addEventListener('input', function(e) {
  const query = e.target.value.toLowerCase();
  
  const filtered = allUsers.filter(user => 
    (user.name || '').toLowerCase().includes(query) ||
    (user.phone_number || '').toLowerCase().includes(query) ||
    String(user.id).includes(query)
  );
  
  renderUsers(filtered);
});

/**
 * Render users table
 * 
 * @param {Array} users - Array of user objects to display
 */
function renderUsers(users) {
  const tbody = document.getElementById('usersTableBody');
  tbody.innerHTML = '';
  
  // Handle empty state
  if (users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:3rem;color:var(--text-muted);">No users found</td></tr>';
    return;
  }
  
  // Render each user with staggered animation
  users.forEach((user, index) => {
    const tr = document.createElement('tr');
    tr.style.animationDelay = `${index * 0.05}s`;
    tr.className = 'fade-in';
    tr.innerHTML = `
      <td style="font-weight:600;color:var(--primary)">#${user.id}</td>
      <td>${user.name || 'Unknown'}</td>
      <td style="color:var(--text-muted)">${user.phone_number || '-'}</td>
      <td><span style="background:var(--primary);color:#fff;padding:0.25rem 0.75rem;border-radius:20px;font-size:0.875rem;font-weight:600;">${user.total_chats || 0}</span></td>
    `;
    tbody.appendChild(tr);
  });
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

