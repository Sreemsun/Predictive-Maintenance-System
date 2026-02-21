document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorMsg = document.getElementById('errorMessage');
    const successMsg = document.getElementById('successMessage');
    const buttonText = document.querySelector('.button-text');
    const buttonLoader = document.querySelector('.button-loader');

    // Hide previous messages
    errorMsg.style.display = 'none';
    successMsg.style.display = 'none';

    // Validate passwords match
    if (password !== confirmPassword) {
        errorMsg.textContent = 'Passwords do not match!';
        errorMsg.style.display = 'block';
        return;
    }

    // Validate password length
    if (password.length < 6) {
        errorMsg.textContent = 'Password must be at least 6 characters long!';
        errorMsg.style.display = 'block';
        return;
    }

    // Validate username length
    if (username.length < 3) {
        errorMsg.textContent = 'Username must be at least 3 characters long!';
        errorMsg.style.display = 'block';
        return;
    }

    // Show loading state
    buttonText.style.display = 'none';
    buttonLoader.style.display = 'flex';

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        // Hide loading state
        buttonText.style.display = 'inline';
        buttonLoader.style.display = 'none';

        if (response.ok && data.success) {
            successMsg.textContent = data.message || 'Registration successful! Redirecting to login...';
            successMsg.style.display = 'block';
            
            // Clear form
            document.getElementById('registerForm').reset();
            
            // Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            errorMsg.textContent = data.message || 'Registration failed. Please try again.';
            errorMsg.style.display = 'block';
        }
    } catch (error) {
        // Hide loading state
        buttonText.style.display = 'inline';
        buttonLoader.style.display = 'none';
        
        errorMsg.textContent = 'An error occurred. Please try again.';
        errorMsg.style.display = 'block';
        console.error('Registration error:', error);
    }
});

// Real-time password matching feedback
document.getElementById('confirmPassword').addEventListener('input', (e) => {
    const password = document.getElementById('password').value;
    const confirmPassword = e.target.value;
    const errorMsg = document.getElementById('errorMessage');

    if (confirmPassword.length > 0 && password !== confirmPassword) {
        errorMsg.textContent = 'Passwords do not match';
        errorMsg.style.display = 'block';
    } else {
        errorMsg.style.display = 'none';
    }
});
