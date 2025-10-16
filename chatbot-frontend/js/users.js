// Users Page JS - Fetches and renders users table

let allUsers = []; // Store all users for search

document.addEventListener('DOMContentLoaded', async function() {
  // Auth check
  if (!localStorage.getItem('token')) {
    window.location.href = 'index.html';
    return;
  }
  
  const tbody = document.getElementById('usersTableBody');
  
  try {
    const res = await fetch('/api/v1/admin/users', {
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
    
    const data = await res.json();
    
    allUsers = data.users || data;
    
    renderUsers(allUsers);
    
    // Success toast
    Toastify({
      text: `Loaded ${allUsers.length} users`,
      duration: 2000,
      gravity: "top",
      position: "right",
      style: {
        background: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)",
      }
    }).showToast();
    
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:3rem;color:var(--error);">Error loading users. Please try again.</td></tr>';
    
    Toastify({
      text: "Failed to load users",
      duration: 3000,
      gravity: "top",
      position: "right",
      style: {
        background: "linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%)",
      }
    }).showToast();
  }
});

// Search functionality
document.getElementById('searchUsers').addEventListener('input', function(e) {
  const query = e.target.value.toLowerCase();
  const filtered = allUsers.filter(user => 
    (user.name || '').toLowerCase().includes(query) ||
    (user.phone_number || '').toLowerCase().includes(query) ||
    String(user.id).includes(query)
  );
  renderUsers(filtered);
});

function renderUsers(users) {
  const tbody = document.getElementById('usersTableBody');
  tbody.innerHTML = '';
  
  if (users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:3rem;color:var(--text-muted);">No users found</td></tr>';
    return;
  }
  
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

