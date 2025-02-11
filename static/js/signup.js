document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signupForm');
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

    // Username availability check
    let usernameTimeout;
    const signupUsername = document.getElementById('signupUsername');
    
    signupUsername.addEventListener('input', function() {
        clearTimeout(usernameTimeout);
        const username = this.value;

        if (!username) return;

        usernameTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`${API_URL}/check-username`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ TenDangNhap: username })
                });

                const data = await response.json();

                if (data.exists) {
                    showError('Tên đăng nhập đã tồn tại');
                    signupUsername.classList.add('error');
                } else {
                    signupUsername.classList.remove('error');
                    removeMessages();
                }
            } catch (error) {
                console.error('Username check failed:', error);
            }
        }, 500);
    });

    // Email availability check
    let emailTimeout;
    const signupEmail = document.getElementById('signupEmail');
    
    signupEmail.addEventListener('input', function() {
        clearTimeout(emailTimeout);
        const email = this.value;

        if (!email || !validateEmail(email)) return;

        emailTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`${API_URL}/check-email`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ Email: email })
                });

                const data = await response.json();

                if (data.exists) {
                    showError('Email đã được sử dụng');
                    signupEmail.classList.add('error');
                } else {
                    signupEmail.classList.remove('error');
                    removeMessages();
                }
            } catch (error) {
                console.error('Email check failed:', error);
            }
        }, 500);
    });

    // Password confirmation check
    const password = document.getElementById('signupPassword');
    const confirmPassword = document.getElementById('confirmPassword');

    confirmPassword.addEventListener('input', function() {
        if (this.value && this.value !== password.value) {
            this.classList.add('error');
        } else {
            this.classList.remove('error');
        }
    });

    // Sign up form submission
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = signupUsername.value.trim();
        const email = signupEmail.value.trim();
        const password = document.getElementById('signupPassword').value;
        const passwordConfirm = confirmPassword.value;
        
        // Validation
        if (!username || !email || !password || !passwordConfirm) {
            showError('Vui lòng điền đầy đủ thông tin');
            return;
        }

        if (username.length < 3) {
            showError('Tên đăng nhập phải có ít nhất 3 ký tự');
            return;
        }

        if (!validateEmail(email)) {
            showError('Email không hợp lệ');
            return;
        }
        
        if (password.length < 6) {
            showError('Mật khẩu phải có ít nhất 6 ký tự');
            return;
        }
        
        if (password !== passwordConfirm) {
            showError('Mật khẩu nhập lại không khớp');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    TenDangNhap: username,
                    Email: email,
                    MatKhau: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Đăng ký thất bại');
            }

            showSuccess('Đăng ký thành công! Đang chuyển hướng...');
            signupForm.reset();

            // Store user data
            localStorage.setItem('user', JSON.stringify(data.user));

            // Redirect to login page after successful registration
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);

        } catch (error) {
            showError(error.message);
        }
    });

    // Social signup buttons
    const socialButtons = document.querySelectorAll('.social-btn');
    socialButtons.forEach(button => {
        button.addEventListener('click', () => {
            const platform = button.classList.contains('google') ? 'Google' : 'Facebook';
            showError(`${platform} signup is not implemented yet`);
        });
    });
});

// Email validation helper
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Error message helper
function showError(message) {
    removeMessages();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message error';
    errorDiv.textContent = message;
    
    const signupForm = document.getElementById('signupForm');
    signupForm.insertBefore(errorDiv, signupForm.firstChild);
    
    setTimeout(removeMessages, 3000);
}

// Success message helper
function showSuccess(message) {
    removeMessages();
    
    const successDiv = document.createElement('div');
    successDiv.className = 'message success';
    successDiv.textContent = message;
    
    const signupForm = document.getElementById('signupForm');
    signupForm.insertBefore(successDiv, signupForm.firstChild);
    
    setTimeout(removeMessages, 3000);
}

// Remove all message elements
function removeMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => message.remove());
}