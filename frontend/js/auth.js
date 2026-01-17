
document.addEventListener("DOMContentLoaded", () => {
    // Login Handling
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const errorDiv = document.getElementById("error-msg");

            try {
                // Since OAuth2PasswordRequestForm expects form data
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);

                const response = await fetch("http://localhost:8000/api/auth/login", {
                    method: "POST",
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error("Login failed");
                }

                const data = await response.json();
                Api.token = data.access_token;
                window.location.href = "dashboard.html";
            } catch (err) {
                errorDiv.textContent = "Invalid email or password";
                errorDiv.classList.remove("hidden");
            }
        });
    }

    // Register Handling
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const errorDiv = document.getElementById("error-msg");

            try {
                await Api.post("/auth/register", { email, password });
                // Auto login after register or redirect to login
                window.location.href = "login.html";
                alert("Registration successful! Please login.");
            } catch (err) {
                errorDiv.textContent = err.message;
                errorDiv.classList.remove("hidden");
            }
        });
    }
});
