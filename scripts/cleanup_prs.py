"""
cleanup_prs.py — Documents obsolete/discarded pull requests for the MauroSalles/Teste repository.

These PRs were closed without merge as part of the PR #26 clean-up initiative
(branch: copilot/cleanup-obsolete-prs). All features from relevant PRs were
consolidated into PR #25 (master consolidation).

Usage:
    python scripts/cleanup_prs.py
"""

DISCARDED_PRS = [
    {
        "number": 1,
        "title": "Gelateria v2.0: connection pooling, new commands, frontend bug fixes",
        "base_sha": "6943f26",
        "reason": "Superseded by PR #22 (merged) and PR #25 — connection pooling, new commands "
                  "and frontend fixes are already in main.",
    },
    {
        "number": 13,
        "title": "Add Stripe, PIX, and PayPal payment integration",
        "base_sha": "b3924fc9",
        "reason": "Stale base (b3924fc9). Payment functionality absorbed into PR #25 "
                  "(master consolidation).",
    },
    {
        "number": 14,
        "title": "Add AI + ML: chatbot, recommendations, forecasting, churn, segmentation, sentiment",
        "base_sha": "b3924fc9",
        "reason": "Stale base (b3924fc9). AI/ML features absorbed into PR #25.",
    },
    {
        "number": 15,
        "title": "Add multi-channel notification engine (email, SMS, push, WebSocket, smart timing)",
        "base_sha": "b3924fc9",
        "reason": "Stale base (b3924fc9). Notification engine absorbed into PR #25.",
    },
    {
        "number": 17,
        "title": "Add Loyalty System: Referral codes + profit-protected coupon engine",
        "base_sha": "b3924fc9",
        "reason": "Stale base (b3924fc9). Loyalty/coupon system absorbed into PR #25.",
    },
    {
        "number": 18,
        "title": "Add Instagram, WhatsApp & AR social commerce integration",
        "base_sha": "b3924fc9",
        "reason": "Stale base (b3924fc9). Social commerce features absorbed into PR #25.",
    },
    {
        "number": 23,
        "title": "[WIP] Clean up repository and professionalize README",
        "base_sha": "03af3ec1",
        "reason": "Stale base (03af3ec1). README professionalisation is covered by PR #25 "
                  "and further refined in PR #26.",
    },
]


def print_report():
    """Print a summary of all discarded pull requests."""
    print("=" * 70)
    print("  DISCARDED PULL REQUESTS — MauroSalles/Teste")
    print("  Reason: superseded / stale base / absorbed by PR #25 or #26")
    print("=" * 70)
    for pr in DISCARDED_PRS:
        print(f"\n  PR #{pr['number']} — {pr['title']}")
        print(f"  Base SHA : {pr['base_sha']}")
        print(f"  Reason   : {pr['reason']}")
    print("\n" + "=" * 70)
    print(f"  Total discarded: {len(DISCARDED_PRS)} PRs")
    print("=" * 70)


if __name__ == "__main__":
    print_report()
