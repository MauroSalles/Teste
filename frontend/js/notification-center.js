/**
 * NotificationCenter — real-time multi-channel notification hub.
 *
 * Connects to the backend via Socket.IO and displays toast-style
 * notifications in the #notification-center element.
 */
class NotificationCenter {
    constructor() {
        this.notifications = [];
        this.preferences = {};
        this.socket = null;
        this._nextId = 1;
        this.init();
    }

    init() {
        this.loadPreferences();
        this.initWebSocket();
        this.setupUI();
    }

    // ------------------------------------------------------------------
    // Preferences
    // ------------------------------------------------------------------

    loadPreferences() {
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        fetch('/api/notifications/preferences', {
            headers: { Authorization: `Bearer ${token}` }
        })
            .then(r => r.json())
            .then(prefs => { this.preferences = prefs; })
            .catch(err => console.warn('Could not load notification preferences:', err));
    }

    savePreferences(prefs) {
        const token = localStorage.getItem('auth_token');
        if (!token) return Promise.reject(new Error('Not authenticated'));

        return fetch('/api/notifications/preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(prefs)
        }).then(r => r.json());
    }

    // ------------------------------------------------------------------
    // WebSocket
    // ------------------------------------------------------------------

    initWebSocket() {
        if (typeof io === 'undefined') {
            console.warn('Socket.IO client not loaded — real-time notifications disabled.');
            return;
        }

        const userId = localStorage.getItem('user_id');
        this.socket = io(window.location.origin, {
            query: { user_id: userId },
            reconnectionAttempts: 5
        });

        this.socket.on('connect', () => {
            console.info('NotificationCenter: connected to real-time channel.');
        });

        this.socket.on('order_update', (data) => {
            this.addNotification({
                type: 'order_update',
                icon: '📦',
                title: `Pedido #${data.order_id}`,
                message: data.status,
                action: () => { window.location.href = `/order/${data.order_id}`; }
            });
        });

        this.socket.on('new_recommendation', (data) => {
            this.addNotification({
                type: 'recommendation',
                icon: '🍓',
                title: data.name,
                message: data.reason,
                image: data.image_url,
                action: () => { window.location.href = `/flavor/${data.flavor_id}`; }
            });
        });

        this.socket.on('live_deal', (data) => {
            this.addNotification({
                type: 'deal',
                icon: '🔥',
                title: `${data.discount}% OFF em ${data.flavor}`,
                message: `Válido por ${data.expires_in_seconds} segundos!`,
                urgency: data.urgency,
                countdown: data.expires_in_seconds
            });
        });

        this.socket.on('disconnect', () => {
            console.info('NotificationCenter: disconnected.');
        });
    }

    // ------------------------------------------------------------------
    // Notification management
    // ------------------------------------------------------------------

    addNotification(notification) {
        notification.id = this._nextId++;
        this.notifications.unshift(notification);
        this.renderNotification(notification);
        this.playSound(notification.type);

        // Auto-dismiss after 5 s except for countdown deals
        if (notification.type !== 'deal') {
            setTimeout(() => this.removeNotification(notification.id), 5000);
        }
    }

    removeNotification(id) {
        this.notifications = this.notifications.filter(n => n.id !== id);
        const el = document.getElementById(`notif-${id}`);
        if (el) {
            el.classList.add('fade-out');
            setTimeout(() => el.remove(), 300);
        }
    }

    renderNotification(notification) {
        const container = document.getElementById('notification-center');
        if (!container) return;

        const urgencyClass = notification.urgency ? ` urgency-${notification.urgency.toLowerCase()}` : '';
        const imageHtml = notification.image
            ? `<img src="${this._escapeHtml(notification.image)}" class="notif-image" alt="">`
            : '';

        const html = `
            <div id="notif-${notification.id}"
                 class="notification ${this._escapeHtml(notification.type)}${urgencyClass}"
                 role="alert" aria-live="polite">
                <span class="icon" aria-hidden="true">${notification.icon}</span>
                ${imageHtml}
                <div class="content">
                    <strong>${this._escapeHtml(notification.title)}</strong>
                    <p>${this._escapeHtml(notification.message)}</p>
                </div>
                <button class="close"
                        aria-label="Fechar notificação"
                        onclick="notificationCenter.removeNotification(${notification.id})">×</button>
            </div>`;

        container.insertAdjacentHTML('afterbegin', html);
    }

    playSound(type) {
        const sounds = {
            order_update:   'notification.mp3',
            deal:           'alert.mp3',
            recommendation: 'ding.mp3'
        };

        const file = sounds[type];
        if (!file) return;

        try {
            const audio = new Audio(`/sounds/${file}`);
            audio.volume = 0.4;
            audio.play().catch(() => { /* Autoplay blocked — ignore */ });
        } catch (e) {
            // Audio not supported
        }
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    _escapeHtml(str) {
        if (str == null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    setupUI() {
        // Ensure the notification container exists
        if (!document.getElementById('notification-center')) {
            const div = document.createElement('div');
            div.id = 'notification-center';
            div.setAttribute('aria-label', 'Notificações');
            document.body.appendChild(div);
        }
    }
}

// Initialise on DOM ready
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        window.notificationCenter = new NotificationCenter();
    });
}
