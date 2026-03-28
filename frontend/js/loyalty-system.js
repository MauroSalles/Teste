/* frontend/js/loyalty-system.js — Referral + Coupon UI */

class LoyaltySystem {
    constructor() {
        this.userCoupons = [];
        this.referralCode = null;
        this.init();
    }

    async init() {
        await this.loadReferralCode();
        await this.loadActiveCoupons();
        this.renderUI();
    }

    async loadReferralCode() {
        try {
            const response = await fetch('/api/loyalty/referral/code', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (!response.ok) return;
            const data = await response.json();
            this.referralCode = data.code;
        } catch (e) {
            console.error('Erro ao carregar código de referência', e);
        }
    }

    async loadActiveCoupons() {
        try {
            const response = await fetch('/api/loyalty/coupons/active', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (!response.ok) return;
            const data = await response.json();
            this.userCoupons = data.coupons || [];
        } catch (e) {
            console.error('Erro ao carregar cupons', e);
        }
    }

    async applyCoupon(couponCode, orderTotal) {
        // STEP 1: Valida
        const validation = await fetch('/api/loyalty/coupon/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ coupon_code: couponCode, order_total: orderTotal })
        });

        const validationResult = await validation.json();
        if (!validationResult.valid) {
            alert(`❌ ${validationResult.error}`);
            return false;
        }

        // STEP 2: Mostra desconto antes de confirmar
        const newTotal = validationResult.new_total;
        const savings = validationResult.discount_amount;

        const confirmed = window.confirm(
            `💰 Você vai economizar R$${savings.toFixed(2)}!\n` +
            `Novo total: R$${newTotal.toFixed(2)}\n\n` +
            `Cupom restante: ${validationResult.coupon_uses_remaining} uso(s)`
        );

        if (!confirmed) return false;

        return validationResult;
    }

    _escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    renderUI() {
        const container = document.getElementById('loyalty-container');
        if (!container) return;

        const safeCode = this._escapeHtml(this.referralCode || '');

        const couponsHtml = this.userCoupons.length > 0 ? `
            <div class="coupons-section">
                <h3>🎟️ Seus Coupons</h3>
                ${this.userCoupons.map(c => `
                    <div class="coupon-card ${this._escapeHtml(c.tier_level)}">
                        <span class="tier-badge">${this._escapeHtml(c.tier_level).replace('_', ' ').toUpperCase()}</span>
                        <strong>${this._escapeHtml(c.code)}</strong>
                        <p>${c.discount_percentage != null ? `${Number(c.discount_percentage).toFixed(0)}% OFF` : this._escapeHtml(c.discount_type)}</p>
                        <small>Válido até ${new Date(c.valid_until).toLocaleDateString('pt-BR')}</small>
                        <small>${c.remaining_uses} uso(s) restante(s)</small>
                    </div>
                `).join('')}
            </div>
        ` : '';

        container.innerHTML = `
            <div class="loyalty-widget">
                <div class="referral-section">
                    <h3>🎁 Seu Código de Referência</h3>
                    <div class="code-box">
                        <input type="text" value="${safeCode}" readonly>
                        <button onclick="navigator.clipboard.writeText(document.querySelector('.code-box input').value)">
                            Copiar
                        </button>
                    </div>
                    <p>Compartilhe com amigos e ganhe créditos!</p>
                </div>
                ${couponsHtml}
            </div>
        `;
    }
}
