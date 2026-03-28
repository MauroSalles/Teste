class ChatbotWidget {
    constructor() {
        this.messages = [];
        this.isOpen = false;
        this.init();
    }

    init() {
        this.createWidget();
        this.attachEventListeners();
    }

    createWidget() {
        const widget = document.createElement('div');
        widget.id = 'chatbot-widget';
        widget.innerHTML = `
            <div class="chatbot-bubble" id="chatbot-toggle">
                <span>💬</span>
            </div>
            <div class="chatbot-window" id="chatbot-window" style="display:none">
                <div class="chatbot-header">
                    <h3>Assistente Gelateria</h3>
                    <button id="chatbot-close">✕</button>
                </div>
                <div class="chatbot-messages" id="chatbot-messages"></div>
                <div class="chatbot-input">
                    <input type="text" id="chatbot-input" placeholder="Pergunte algo...">
                    <button id="chatbot-send">→</button>
                </div>
            </div>
        `;
        document.body.appendChild(widget);
    }

    attachEventListeners() {
        document.getElementById('chatbot-toggle').addEventListener('click', () => this.toggle());
        document.getElementById('chatbot-close').addEventListener('click', () => this.close());
        document.getElementById('chatbot-send').addEventListener('click', () => this.sendMessage());
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        this.addMessage('user', message);
        input.value = '';

        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, history: this.messages }),
            });

            const data = await response.json();
            if (data.success) {
                this.addMessage('bot', data.response);
            } else {
                this.addMessage('bot', 'Desculpe, erro ao processar. Tente novamente!');
            }
        } catch (error) {
            this.addMessage('bot', 'Desculpe, erro ao processar. Tente novamente!');
        }
    }

    addMessage(role, text) {
        this.messages.push({ role, text });
        const messagesDiv = document.getElementById('chatbot-messages');
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${role}`;
        messageEl.textContent = text;
        messagesDiv.appendChild(messageEl);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    toggle() {
        this.isOpen = !this.isOpen;
        document.getElementById('chatbot-window').style.display = this.isOpen ? 'flex' : 'none';
    }

    close() {
        this.isOpen = false;
        document.getElementById('chatbot-window').style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatbotWidget();
});
