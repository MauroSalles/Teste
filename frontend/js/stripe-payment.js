// frontend/js/stripe-payment.js
// Requires Stripe.js loaded via <script src="https://js.stripe.com/v3/"></script>

class StripePayment {
    constructor() {
        this.stripe = Stripe(window.STRIPE_PUBLIC_KEY);
        this.elements = this.stripe.elements();
        this.cardElement = this.elements.create('card');
    }

    mountCard(selector) {
        this.cardElement.mount(selector);
    }

    async createPayment(amount, orderId) {
        try {
            const response = await fetch('/api/payments/stripe/intent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this._getToken()}`
                },
                body: JSON.stringify({ amount, order_id: orderId })
            });

            if (!response.ok) {
                const err = await response.json();
                return { success: false, error: err.error || 'Failed to create payment intent' };
            }

            const { client_secret } = await response.json();

            const result = await this.stripe.confirmCardPayment(client_secret, {
                payment_method: {
                    card: this.cardElement,
                    billing_details: { name: 'Customer' }
                }
            });

            if (result.error) {
                return { success: false, error: result.error.message };
            }

            if (result.paymentIntent.status === 'succeeded') {
                return { success: true, payment_id: result.paymentIntent.id };
            }

            return { success: false, error: 'Payment not completed' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    _getToken() {
        return localStorage.getItem('auth_token') || '';
    }
}
