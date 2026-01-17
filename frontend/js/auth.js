
document.addEventListener("DOMContentLoaded", () => {
    // Login Handling
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value.trim();
            const errorDiv = document.getElementById("error-msg");

            try {
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);

                const data = await Api.post("/auth/login", formData);

                Api.token = data.access_token;
                window.location.href = "dashboard.html";
            } catch (err) {
                if (window.UI) {
                    UI.notify("Неверный email или пароль", "error");
                }
                errorDiv.textContent = "Неверный email или пароль";
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
            const confirmPassword = document.getElementById("confirm_password") ? document.getElementById("confirm_password").value : "";
            const fullName = document.getElementById("full_name") ? document.getElementById("full_name").value : "";
            const errorDiv = document.getElementById("error-msg");

            if (confirmPassword && password !== confirmPassword) {
                const msg = "Пароли не совпадают";
                if (window.UI) UI.notify(msg, "error");
                errorDiv.textContent = msg;
                errorDiv.classList.remove("hidden");
                return;
            }

            try {
                await Api.post("/auth/register", {
                    email,
                    password,
                    full_name: fullName
                });

                if (window.UI) {
                    UI.notify("Регистрация успешна!", "success");
                }

                setTimeout(() => {
                    window.location.href = "login.html";
                }, 1500);
            } catch (err) {
                if (window.UI) {
                    UI.notify(err.message, "error");
                }
                errorDiv.textContent = err.message;
                errorDiv.classList.remove("hidden");
            }
        });
    }
});
