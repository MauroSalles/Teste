// frontend/js/pix-payment.js

class PIXPayment {
    constructor() {
        this.pollInterval = null;
    }

    async generateQRCode(orderId, amount) {
        try {
            const response = await fetch('/api/payments/pix/qrcode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this._getToken()}`
                },
                body: JSON.stringify({ order_id: orderId, amount })
            });

            const data = await response.json();

            if (data.success) {
                // qrCode is server-generated (from Braspag API), not user input.
                this.displayQRCode(data.qr_code, data.copy_paste);
                this.pollPaymentStatus(data.transaction_id);
            } else {
                console.error('PIX error:', data.error);
            }
        } catch (error) {
            console.error('PIX error:', error);
        }
    }

    displayQRCode(qrCode, copyPaste) {
        const container = document.getElementById('pix-qr-container');
        if (!container) return;

        // Escape copyPaste for safe HTML attribute insertion
        const safeCopyPaste = this._escapeHtml(copyPaste);

        container.innerHTML = `
            <div class="pix-widget">
                <h3>Escaneie o QR Code</h3>
                <img src="data:image/svg+xml;base64,${btoa(qrCode)}" alt="PIX QR Code">
                <p>Ou copie e cole:</p>
                <input type="text" id="pix-copy-input" value="${safeCopyPaste}" readonly>
                <button id="pix-copy-btn">Copiar</button>
            </div>
        `;

        document.getElementById('pix-copy-btn').addEventListener('click', () => {
            navigator.clipboard.writeText(copyPaste);
        });
    }

    async pollPaymentStatus(transactionId) {
        const checkStatus = async () => {
            try {
                const response = await fetch(`/api/payments/pix/status/${encodeURIComponent(transactionId)}`, {
                    headers: { 'Authorization': `Bearer ${this._getToken()}` }
                });
                const data = await response.json();

                if (data.paid) {
                    const statusEl = document.getElementById('pix-status');
                    if (statusEl) statusEl.textContent = '✅ Pagamento confirmado!';
                    clearInterval(this.pollInterval);
                }
            } catch (error) {
                console.error('PIX status check error:', error);
            }
        };

        this.pollInterval = setInterval(checkStatus, 2000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    _getToken() {
        return localStorage.getItem('auth_token') || '';
    }

    _escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
}
