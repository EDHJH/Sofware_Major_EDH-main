document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const passwordInput = document.getElementById('password');
    const passwordIcon = document.querySelector('.register__password');

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
    registerForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            firstname: document.getElementById('firstname').value,
            lastname: document.getElementById('lastname').value,
            email: document.getElementById('email').value,
            password: passwordInput.value
        };

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            if (data.success) {
                window.location.href = '/';
            } else {
                alert('Registration failed: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during registration');
        }
    });
});
