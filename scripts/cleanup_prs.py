"""
cleanup_prs.py — Documentation of discarded PRs and the rationale for each decision.

This file is NOT meant to be executed via the API. It serves as an audit trail
recording which pull requests were deliberately discarded during project consolidation
and which PR absorbed their content (if any).
"""

DISCARDED_PRS: dict[int, dict] = {
    1: {
        "title": "Initial project scaffold",
        "reason_discarded": "Superseded by the full project structure introduced in PR #2.",
        "absorbed_by": 2,
    },
    3: {
        "title": "Add basic sabores endpoint",
        "reason_discarded": (
            "Functionality was re-implemented with proper DB pooling and error handling "
            "in the api_routes refactor (PR #5)."
        ),
        "absorbed_by": 5,
    },
    7: {
        "title": "Prototype payment flow (no Stripe)",
        "reason_discarded": (
            "Replaced by the full Stripe + PIX integration introduced in PR #10."
        ),
        "absorbed_by": 10,
    },
    12: {
        "title": "Simple auth with plain-text passwords",
        "reason_discarded": (
            "Security concern: plain-text passwords. "
            "Proper JWT-based auth with hashed passwords was introduced in PR #14."
        ),
        "absorbed_by": 14,
    },
    17: {
        "title": "Loyalty system v0 (no gamification)",
        "reason_discarded": (
            "Merged into the combined loyalty + gamification feature in PR #20."
        ),
        "absorbed_by": 20,
    },
    19: {
        "title": "Standalone gamification PR",
        "reason_discarded": (
            "Merged together with the loyalty system in PR #20 to avoid circular imports "
            "and keep the codebase consistent."
        ),
        "absorbed_by": 20,
    },
    22: {
        "title": "Notification service (email only)",
        "reason_discarded": (
            "Extended to include WhatsApp and Instagram channels in PR #24 "
            "before the notification_routes were finalised."
        ),
        "absorbed_by": 24,
    },
    25: {
        "title": "Landing page and health endpoint (first attempt)",
        "reason_discarded": (
            "Incomplete implementation — missing status page, cmd commands, "
            "Makefile, and full .env.example. "
            "All features were re-implemented and completed in PR #26."
        ),
        "absorbed_by": 26,
    },
}


if __name__ == "__main__":
    print("Discarded PRs summary")
    print("=" * 60)
    for pr_num, info in DISCARDED_PRS.items():
        absorbed = info.get("absorbed_by")
        print(f"\nPR #{pr_num}: {info['title']}")
        print(f"  Reason    : {info['reason_discarded']}")
        print(f"  Absorbed  : PR #{absorbed}" if absorbed else "  Absorbed  : N/A (fully discarded)")
