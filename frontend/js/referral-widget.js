/**
 * ReferralWidget — Programa de Referência
 * Exibe progresso, compartilhamento e leaderboard de referências.
 */
class ReferralWidget {
    constructor(userId, containerId) {
        this.userId = userId;
        this.containerId = containerId || 'referral-section';
        this.dashboard = null;
        this.init();
    }

    async init() {
        try {
            const response = await fetch(`/api/referral/dashboard/${this.userId}`);
            const data = await response.json();
            if (data.success) {
                this.dashboard = data.dashboard;
                this.render();
                await this.loadLeaderboard();
            } else {
                this._renderError(data.error || 'Erro ao carregar dashboard');
            }
        } catch (err) {
            this._renderError('Erro de conexão: ' + err.message);
        }
    }

    render() {
        const d = this.dashboard;
        const stats = d.stats;
        const progress = d.progress;

        const container = document.getElementById(this.containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="referral-widget">
                <h2>💰 Programa de Referência</h2>

                <div class="referral-code-box">
                    <span class="label">Seu código:</span>
                    <span class="code">${d.referral_code}</span>
                    <button class="copy-btn" id="copy-code-btn">Copiar código</button>
                </div>

                <div class="referral-progress">
                    <div class="milestone-tracker">
                        <div class="milestone ${stats.total_conversions >= 1 ? 'completed' : ''}">
                            <span class="icon">🌱</span>
                            <span class="label">1 Amigo</span>
                        </div>
                        <div class="milestone ${stats.total_conversions >= 5 ? 'completed' : (stats.total_conversions >= 1 ? 'active' : '')}">
                            <span class="icon">🌿</span>
                            <span class="label">5 Amigos</span>
                            <span class="reward">15% OFF</span>
                        </div>
                        <div class="milestone ${stats.total_conversions >= 10 ? 'completed' : ''}">
                            <span class="icon">🌳</span>
                            <span class="label">10 Amigos</span>
                            <span class="reward">AÇAÍ GRÁTIS</span>
                        </div>
                    </div>

                    <div class="progress-bar">
                        <div class="fill" style="width: ${Math.min(progress.progress_percent, 100)}%"></div>
                        <span class="progress-label">${stats.total_conversions} / ${progress.next_milestone}</span>
                    </div>
                </div>

                <div class="referral-actions">
                    <button class="share-btn whatsapp" id="share-whatsapp">WhatsApp</button>
                    <button class="share-btn instagram" id="share-instagram">Instagram</button>
                    <button class="share-btn email" id="share-email">Email</button>
                    <button class="share-btn facebook" id="share-facebook">Facebook</button>
                </div>

                <div class="stats">
                    <div class="stat">
                        <span class="value">${stats.total_conversions}</span>
                        <span class="label">Amigos indicados</span>
                    </div>
                    <div class="stat">
                        <span class="value">${stats.confirmed_conversions}</span>
                        <span class="label">Confirmados</span>
                    </div>
                    <div class="stat">
                        <span class="value">${stats.pending_conversions}</span>
                        <span class="label">Pendentes</span>
                    </div>
                </div>

                <div class="leaderboard-preview">
                    <h3>🏆 Top Referrers do Mês</h3>
                    <div id="leaderboard-container">Carregando...</div>
                </div>
            </div>
        `;

        this._attachEvents();
    }

    _attachEvents() {
        const d = this.dashboard;

        const copyBtn = document.getElementById('copy-code-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyCode());
        }

        const shareMap = {
            'share-whatsapp': 'whatsapp',
            'share-instagram': 'instagram',
            'share-email': 'email',
            'share-facebook': 'facebook',
        };

        Object.entries(shareMap).forEach(([id, platform]) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', () => this.shareVia(platform));
            }
        });
    }

    shareVia(platform) {
        const templates = this.dashboard.share_templates;
        const message = templates[platform];

        switch (platform) {
            case 'whatsapp':
                window.open(`https://wa.me/?text=${encodeURIComponent(message)}`, '_blank');
                break;
            case 'email':
                window.location.href = `mailto:?subject=Achei um lugar incrível de açaí!&body=${encodeURIComponent(message)}`;
                break;
            case 'instagram':
                navigator.clipboard.writeText(message).then(() => {
                    alert('Texto copiado! Cole nas suas stories do Instagram 📸\n\n' + message);
                });
                break;
            case 'facebook':
                window.open(`https://www.facebook.com/sharer/sharer.php?quote=${encodeURIComponent(message)}`, '_blank');
                break;
        }
    }

    copyCode() {
        const code = this.dashboard.referral_code;
        navigator.clipboard.writeText(code).then(() => {
            alert('Código copiado! 🎉 ' + code);
        }).catch(() => {
            prompt('Copie seu código:', code);
        });
    }

    async loadLeaderboard() {
        try {
            const response = await fetch('/api/referral/leaderboard?limit=5');
            const data = await response.json();
            const container = document.getElementById('leaderboard-container');
            if (!container) return;

            if (data.success && data.leaderboard.length > 0) {
                const rows = data.leaderboard.map((entry, i) => `
                    <div class="leaderboard-row">
                        <span class="rank">#${i + 1}</span>
                        <span class="user-id">Usuário ${entry.id}</span>
                        <span class="count">${entry.confirmed_referrals} confirmados</span>
                    </div>
                `).join('');
                container.innerHTML = rows;
            } else {
                container.innerHTML = '<p>Nenhum referrer este mês. Seja o primeiro! 🚀</p>';
            }
        } catch (err) {
            const container = document.getElementById('leaderboard-container');
            if (container) container.innerHTML = '<p>Erro ao carregar leaderboard.</p>';
        }
    }

    _renderError(message) {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `<div class="referral-error">⚠️ ${message}</div>`;
        }
    }
}
