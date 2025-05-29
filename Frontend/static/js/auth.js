function toggleForm(event) {
    event.preventDefault();
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    loginForm.classList.toggle('active');
    registerForm.classList.toggle('active');
}

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.querySelector('input[type="email"]').value;
    const password = form.querySelector('input[type="password"]').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (data.success) {
            window.location.replace('/dashboard');
        } else {
            showError('Login failed: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('An error occurred during login. Please try again.');
    }
}

function validatePassword(password) {
    const minLength = password.length >= 10;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?_":{}|<>]/.test(password); // Fixed to match backend
    
    return {
        isValid: minLength && hasUpperCase && hasLowerCase && hasNumber && hasSpecial,
        errors: {
            minLength,
            hasUpperCase,
            hasLowerCase,
            hasNumber,
            hasSpecial
        }
    };
}

function validatePasswordRequirement(password) {
    const requirements = {
        length: password.length >= 10,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[!@#$%^&*(),.?_":{}|<>]/.test(password) // Fixed to match backend
    };

    Object.entries(requirements).forEach(([key, valid]) => {
        const requirement = document.querySelector(`[data-requirement="${key}"]`);
        if (requirement) {
            requirement.classList.toggle('valid', valid);
        }
    });

    return Object.values(requirements).every(Boolean);
}

function sanitizeText(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    // Replace alert with better UI feedback
    const sanitizedMessage = sanitizeText(message);
    
    // Remove existing error messages
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Create error element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = sanitizedMessage;
    errorDiv.style.cssText = `
        background-color: #fee;
        color: #c33;
        padding: 10px;
        border: 1px solid #fcc;
        border-radius: 4px;
        margin: 10px 0;
        font-size: 14px;
    `;
    
    // Insert at the top of the active form
    const activeForm = document.querySelector('.form-box.active');
    if (activeForm) {
        activeForm.insertBefore(errorDiv, activeForm.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const username = form.querySelector('input[type="text"]').value;
    const email = form.querySelector('input[type="email"]').value;
    const password = form.querySelector('input[type="password"]').value;

    if (!validatePasswordRequirement(password)) {
        return;
    }

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();
        if (data.success) {
            window.location.replace('/dashboard');
        } else {
            showError('Registration failed: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('An error occurred during registration. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Add password toggle functionality for both login and register forms
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    [loginForm, registerForm].forEach(form => {
        const passwordInput = form.querySelector('input[type="password"]');
        const passwordIcon = form.querySelector('.ri-eye-off-fill');

        passwordIcon?.addEventListener('click', () => {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                passwordIcon.classList.replace('ri-eye-off-fill', 'ri-eye-fill');
            } else {
                passwordInput.type = 'password';
                passwordIcon.classList.replace('ri-eye-fill', 'ri-eye-off-fill');
            }
        });
    });

    const registerPassword = document.getElementById('registerPassword');
    if (registerPassword) {
        registerPassword.addEventListener('input', (e) => {
            validatePasswordRequirement(e.target.value);
        });
    }
});
