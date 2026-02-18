document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const loginButton = loginForm.querySelector('button[type="submit"]');
    const buttonText = loginButton.querySelector('.button-text');
    const buttonLoader = loginButton.querySelector('.button-loader');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        // Hide previous errors
        errorMessage.style.display = 'none';

        // Show loading state
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'block';
        loginButton.disabled = true;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (data.success) {
                // Success - redirect to dashboard
                window.location.href = '/dashboard';
            } else {
                // Show error message
                errorMessage.textContent = data.message || 'Invalid username or password';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            errorMessage.textContent = 'An error occurred. Please try again.';
            errorMessage.style.display = 'block';
        } finally {
            // Reset button state
            buttonText.style.display = 'inline';
            buttonLoader.style.display = 'none';
            loginButton.disabled = false;
        }
    });

    // Clear error message on input
    const inputs = loginForm.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            errorMessage.style.display = 'none';
        });
    });
});
