/**
 * UI Utilities for Nexus AI
 * Consistent notifications and common UI helpers
 */

const UI = {
    /**
     * Show a notification message
     * @param {string} message 
     * @param {'success' | 'error' | 'info' | 'warning'} type 
     */
    notify(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) {
            const newContainer = document.createElement('div');
            newContainer.id = 'notification-container';
            newContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            `;
            document.body.appendChild(newContainer);
            this.notify(message, type);
            return;
        }

        const toast = document.createElement('div');
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            info: '#3B82F6',
            warning: '#F59E0B'
        };

        toast.style.cssText = `
            background: white;
            color: #1F2937;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            border-left: 4px solid ${colors[type] || colors.info};
            min-width: 250px;
            max-width: 400px;
            animation: slideIn 0.3s ease-out forwards;
            display: flex;
            align-items: center;
            justify-content: space-between;
        `;

        toast.innerHTML = `
            <span style="font-size: 0.95rem;">${message}</span>
            <button onclick="this.parentElement.remove()" style="
                background: none;
                border: none;
                color: #9CA3AF;
                cursor: pointer;
                margin-left: 10px;
                font-size: 1.2rem;
            ">&times;</button>
        `;

        // Add keyframes if not exists
        if (!document.getElementById('toast-animations')) {
            const style = document.createElement('style');
            style.id = 'toast-animations';
            style.innerHTML = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes fadeOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        container.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease-in forwards';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
};

window.UI = UI;
