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
            window.location.href = '/dashboard';
        } else {
            alert('Login failed: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during login');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const username = form.querySelector('input[type="text"]').value;
    const email = form.querySelector('input[type="email"]').value;
    const password = form.querySelector('input[type="password"]').value;

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                firstname: username,
                lastname: "",
                email,
                password
            })
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = '/dashboard';
        } else {
            alert('Registration failed: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during registration');
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
});
