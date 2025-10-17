/**
 * Login Page - Authentication Handler
 * 
 * Handles admin login form submission, validation, and JWT token storage.
 * Redirects to dashboard on successful authentication.
 */

document.getElementById('loginForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  const errorDiv = document.getElementById('loginError');
  const btn = e.target.querySelector('button[type="submit"]');
  const originalText = btn.textContent;
  
  errorDiv.textContent = '';

  // Validate input fields
  if (!username || !password) {
    showToast("Please enter both username and password", "warning");
    return;
  }

  // Show loading state
  btn.disabled = true;
  btn.innerHTML = '⏳ Logging in...';

  try {
    // Authenticate with backend
    const res = await fetch('/api/v1/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!res.ok) {
      throw new Error('Invalid credentials');
    }
    
    const data = await res.json();
    
    // Store JWT token
    localStorage.setItem('token', data.access_token);
    
    showToast("Login successful! Redirecting...", "success");
    
    // Redirect to dashboard
    setTimeout(() => window.location.href = 'dashboard.html', 1000);
    
  } catch (err) {
    showToast("Invalid username or password", "error");
    
    // Reset button state
    btn.disabled = false;
    btn.textContent = originalText;
  }
});

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
