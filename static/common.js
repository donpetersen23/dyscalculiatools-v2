
// Common JavaScript functions for all pages
function showLogin() {
    document.getElementById('login-modal').style.display = 'block';
}

function showSignup() {
    document.getElementById('signup-modal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function logout() {
    document.getElementById('user-menu').style.display = 'none';
    document.getElementById('auth-btn').style.display = 'block';
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}
