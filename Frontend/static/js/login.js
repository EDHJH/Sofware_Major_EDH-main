document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const passwordInput = document.getElementById('password');
    const passwordIcon = document.querySelector('.login__password');

    // Toggle password visibility
    passwordIcon?.addEventListener('click', () => {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            passwordIcon.classList.replace('ri-eye-off-fill', 'ri-eye-fill');
        } else {
            passwordInput.type = 'password';
            passwordIcon.classList.replace('ri-eye-fill', 'ri-eye-off-fill');
        }
    });

    // Handle form submission
    loginForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = passwordInput.value;

        try {
            const response = await fetch('/login', {
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
    });
});
