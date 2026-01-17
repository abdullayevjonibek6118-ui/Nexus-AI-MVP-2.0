
const API_URL = "http://localhost:8000/api";

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
        } else if (body) {
            headers["Content-Type"] = "application/json";
            fetchOptions.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_URL}${endpoint}`, fetchOptions);
            
            if (response.status === 401) {
                // Determine if we are on a public page
                const path = window.location.pathname;
                if (!path.includes("login.html") && !path.includes("register.html") && !path.includes("index.html") && path !== "/") {
                    this.logout();
                }
                throw new Error("Unauthorized");
            }
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "API Request Failed");
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
