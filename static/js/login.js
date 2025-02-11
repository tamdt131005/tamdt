document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const rememberMe = document.getElementById('remember');
    const API_URL = '/api';

    // Password visibility toggle
    document.querySelectorAll('.toggle-password').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordInput = this.previousElementSibling;
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    });

    // Check for saved login credentials
    const savedCredentials = localStorage.getItem('rememberMe');
    if (savedCredentials) {
        const credentials = JSON.parse(savedCredentials);
        document.getElementById('loginUsername').value = credentials.username;
        rememberMe.checked = true;
    }

    // Login form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('.submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Đang đăng nhập...';
        
        const userInput = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;
        
        try {
            // Basic validation
            if (!userInput) {
                throw new Error('Tên đăng nhập hoặc email không được để trống');
            }
            if (!password) {
                throw new Error('Mật khẩu không được để trống');
            }

            // Determine if input is email or username
            const isEmail = userInput.includes('@');
            
            // Send login request
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ 
                    TenDangNhap: isEmail ? '' : userInput,
                    Email: isEmail ? userInput : '',
                    MatKhau: password,
                    remember_me: rememberMe.checked
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Đăng nhập thất bại. Vui lòng thử lại.');
            }

            // Handle "Remember me" and user data storage
            const userData = {
                TenDangNhap: data.TenDangNhap,
                Quyen: data.Quyen,
                HoTen: data.HoTen
            };

            if (rememberMe.checked && data.remember_token) {
                // Store credentials securely with the token
                localStorage.setItem('rememberMe', JSON.stringify({
                    username: data.TenDangNhap,
                    token: data.remember_token
                }));
            } else {
                localStorage.removeItem('rememberMe');
            }

            // Store current session data
            localStorage.setItem('user', JSON.stringify(userData));
            
            showSuccess('Đăng nhập thành công! Đang chuyển hướng...');

            // Redirect based on user role
            setTimeout(() => {
                const redirectPath = userData.Quyen === 0 ? '/admin' : 
                                   userData.Quyen === 1 ? '/staff' : '/dashboard';
                window.location.href = redirectPath;
            }, 1500);

        } catch (error) {
            console.error('Login error:', error);
            showError(error.message || 'Đã xảy ra lỗi. Vui lòng thử lại.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Đăng nhập';
        }
    });

    // Social login buttons
    const socialButtons = document.querySelectorAll('.social-btn');
    socialButtons.forEach(button => {
        button.addEventListener('click', async () => {
            if (button.classList.contains('google')) {
                try {
                    // Start Google OAuth flow
                    const response = await fetch(`${API_URL}/login/google`);
                    const data = await response.json();
                    
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    
                    // Redirect to Google's consent page
                    window.location.href = data.redirect_url;
                } catch (error) {
                    console.error('Google login error:', error);
                    showError('Đăng nhập bằng Google thất bại. Vui lòng thử lại.');
                }
            } else if (button.classList.contains('facebook')) {
                showError('Facebook login is not implemented yet');
            }
        });
    });
});

// Email validation helper
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Error message helper
function showError(message) {
    removeMessages();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message error';
    errorDiv.textContent = message;
    
    const loginForm = document.getElementById('loginForm');
    loginForm.insertBefore(errorDiv, loginForm.firstChild);
    
    // Scroll to error message
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    setTimeout(removeMessages, 5000);
}

// Success message helper
function showSuccess(message) {
    removeMessages();
    
    const successDiv = document.createElement('div');
    successDiv.className = 'message success';
    successDiv.textContent = message;
    
    const loginForm = document.getElementById('loginForm');
    loginForm.insertBefore(successDiv, loginForm.firstChild);
    
    // Scroll to success message
    successDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    setTimeout(removeMessages, 3000);
}

// Remove all message elements
function removeMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        message.classList.add('fade-out');
        setTimeout(() => message.remove(), 300);
    });
}

// Add CSS styles
document.head.insertAdjacentHTML('beforeend', `
<style>
.message {
    opacity: 1;
    transition: opacity 0.3s ease-out;
}
.message.fade-out {
    opacity: 0;
}
.submit-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}
</style>
`);