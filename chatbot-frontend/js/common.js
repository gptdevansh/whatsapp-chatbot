/**
 * Common JavaScript - Shared Utilities
 * 
 * Handles authentication logout and other shared functionality
 * across all admin pages.
 */

/**
 * Logout user and clear authentication
 */
function logout() {
  if (confirm('Are you sure you want to logout?')) {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
  }
}

/**
 * Initialize common functionality on page load
 */
document.addEventListener('DOMContentLoaded', function() {
  // Attach logout handler if button exists
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function(e) {
      e.preventDefault();
      logout();
    });
  }
});
