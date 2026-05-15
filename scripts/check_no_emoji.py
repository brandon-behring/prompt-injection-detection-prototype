#!/usr/bin/env python3
"""Pre-commit hook: scan files for emoji code points.

Fails (exit 1) if any file in argv contains a code point in the emoji
ranges. Used by `.pre-commit-config.yaml`. Per SPEC_GREENFIELD §5
"no-emoji invariant" + STYLE.md "Anti-style: no emoji in source / docs."
"""

import sys


EMOJI_RANGES = (
    (0x1F000, 0x1FAFF),  # supplemental + extended symbols & pictographs
    (0x2600, 0x27BF),  # misc symbols + dingbats
)


def has_emoji(path: str) -> bool:
    try:
        with open(path, errors="ignore") as f:
            text = f.read()
    except (OSError, UnicodeError):
        return False
    return any(any(lo <= ord(c) <= hi for lo, hi in EMOJI_RANGES) for c in text)


def main() -> int:
    bad = [p for p in sys.argv[1:] if has_emoji(p)]
    if bad:
        print(f"emoji found in: {bad}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
