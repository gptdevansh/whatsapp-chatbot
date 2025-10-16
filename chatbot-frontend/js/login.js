// Login Page JS - Handles form validation and login API call

document.getElementById('loginForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  const errorDiv = document.getElementById('loginError');
  const btn = e.target.querySelector('button[type="submit"]');
  const originalText = btn.textContent;
  errorDiv.textContent = '';

  // Simple validation
  if (!username || !password) {
    Toastify({
      text: "Please enter both username and password",
      duration: 3000,
      gravity: "top",
      position: "right",
      style: {
        background: "linear-gradient(135deg, #ffa94d 0%, #f76707 100%)",
      }
    }).showToast();
    return;
  }

  // Disable button and show loading
  btn.disabled = true;
  btn.innerHTML = '⏳ Logging in...';

  // Call backend login API
  try {
    const res = await fetch('/api/v1/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      throw new Error('Invalid credentials');
    }
    const data = await res.json();
    // Save token (assume JWT)
    localStorage.setItem('token', data.access_token);
    
    // Success toast
    Toastify({
      text: "Login successful! Redirecting...",
      duration: 2000,
      gravity: "top",
      position: "right",
      style: {
        background: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)",
      }
    }).showToast();
    
    setTimeout(() => window.location.href = 'dashboard.html', 1000);
  } catch (err) {
    // Error toast
    Toastify({
      text: "Invalid username or password",
      duration: 3000,
      gravity: "top",
      position: "right",
      style: {
        background: "linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%)",
      }
    }).showToast();
    
    // Re-enable button
    btn.disabled = false;
    btn.textContent = originalText;
  }
});
