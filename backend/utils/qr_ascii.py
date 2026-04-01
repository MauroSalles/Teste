"""QR code ASCII art generator for terminal display."""


def generate_qr_ascii(pix_key: str) -> str:
    """Return a fake but visually authentic QR code ASCII art.
    Uses a deterministic pattern based on pix_key length."""
    import hashlib
    seed = int(hashlib.md5(pix_key.encode()).hexdigest(), 16)
    lines = []
    # Top finder pattern
    lines.append("  █▀▀▀▀▀█  ░░░░  █▀▀▀▀▀█  ")
    lines.append("  █ ███ █  ░░░░  █ ███ █  ")
    lines.append("  █ ███ █  ░░░░  █ ███ █  ")
    lines.append("  █ ███ █  ░░░░  █ ███ █  ")
    lines.append("  █▄▄▄▄▄█  ░░░░  █▄▄▄▄▄█  ")
    # Data area - deterministic based on seed
    for i in range(7):
        row = "  "
        for j in range(25):
            bit = (seed >> ((i * 25 + j) % 64)) & 1
            row += "█" if bit else "░"
        lines.append(row + "  ")
    # Bottom finder pattern
    lines.append("  █▀▀▀▀▀█  " + "░" * 6 + "  ░░░░░░░  ")
    lines.append("  █ ███ █  " + "░" * 6 + "  ░░░░░░░  ")
    lines.append("  █ ███ █  " + "░" * 6 + "  ░░░░░░░  ")
    lines.append("  █ ███ █  " + "░" * 6 + "  ░░░░░░░  ")
    lines.append("  █▄▄▄▄▄█  " + "░" * 6 + "  ░░░░░░░  ")
    return "\n".join(lines)
