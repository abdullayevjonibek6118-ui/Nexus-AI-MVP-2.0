
const API_URL = "http://127.0.0.1:8000/api";

class Api {
    static get token() {
        return localStorage.getItem("access_token");
    }

    static set token(value) {
        localStorage.setItem("access_token", value);
    }

    static logout() {
        localStorage.removeItem("access_token");
        window.location.href = "login.html";
    }

    static async request(endpoint, method = "GET", body = null, isFile = false) {
        const headers = {};
        if (this.token) {
            headers["Authorization"] = `Bearer ${this.token}`;
        }

        let fetchOptions = {
            method,
            headers,
        };

        if (isFile) {
            fetchOptions.body = body; // FormData automatically sets Content-Type
        } else if (body instanceof URLSearchParams) {
            headers["Content-Type"] = "application/x-www-form-urlencoded";
            fetchOptions.body = body;
        } else if (body) {
            headers["Content-Type"] = "application/json";
            fetchOptions.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_URL}${endpoint}`, fetchOptions);

            if (response.status === 401) {
                // Only logout if we're on a protected page AND token exists
                const path = window.location.pathname;
                const isProtectedPage = !path.includes("login.html") && !path.includes("register.html") && !path.includes("index.html") && path !== "/";

                if (isProtectedPage && this.token) {
                    console.warn("Сессия истекла. Пожалуйста, войдите снова.");
                    this.logout();
                }
                throw new Error("Unauthorized");
            }

            if (!response.ok) {
                let errorMsg = "API Request Failed";
                try {
                    const errorData = await response.json();

                    // Handle Subscription Limit Reached
                    if (response.status === 402 && errorData.detail && errorData.detail.error === "SUBSCRIPTION_LIMIT_REACHED") {
                        window.location.href = "pricing.html?error=limit_reached";
                    }

                    if (typeof errorData.detail === 'string') {
                        errorMsg = errorData.detail;
                    } else if (typeof errorData.detail === 'object') {
                        errorMsg = errorData.detail.msg || JSON.stringify(errorData.detail);
                    } else if (errorData.message) {
                        errorMsg = errorData.message;
                    }
                } catch (e) {
                    errorMsg = response.statusText || errorMsg;
                }

                throw new Error(errorMsg);
            }

            return await response.json();
        } catch (error) {
            console.error("API Error:", error);
            throw error;
        }
    }

    static get(endpoint) {
        return this.request(endpoint, "GET");
    }

    static post(endpoint, body) {
        return this.request(endpoint, "POST", body);
    }

    static upload(endpoint, formData) {
        return this.request(endpoint, "POST", formData, true);
    }
}


// Sidebar Toggle logic
function toggleSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    if (sidebar) sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('active');
}
